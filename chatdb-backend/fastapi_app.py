# fastapi_app.py
import os
import re
import random
import numpy as np
import pandas as pd
import mysql.connector
from datetime import timedelta, datetime
from pymongo import MongoClient

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, constr

# =========================
# App & CORS
# =========================
app = FastAPI(title="ChatDB API (FastAPI)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DB Connections / Helpers
# =========================
# Use env vars in real projects; falling back to your current local defaults
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASS = os.getenv("MYSQL_PASS", "dsci@551-Tuesday-Section")
MYSQL_DB   = os.getenv("MYSQL_DB",   "ChatDB")

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB   = os.getenv("MONGO_DB",   "ChatDB")

client = MongoClient(MONGO_HOST, MONGO_PORT)
mongo_db = client[MONGO_DB]

def get_mysql_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, database=MYSQL_DB
    )

def replace_nan_with_none(data):
    if isinstance(data, list):
        return [replace_nan_with_none(item) for item in data]
    elif isinstance(data, dict):
        return {k: replace_nan_with_none(v) for k, v in data.items()}
    elif isinstance(data, float) and np.isnan(data):
        return None
    else:
        return data

# =========================
# Root
# =========================
@app.get("/", response_class=PlainTextResponse)
def index():
    return "Welcome to ChatDB!"

# =========================
# Upload Dataset
# =========================
@app.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    database: constr(strip_whitespace=True) = Form(...),  # "mysql" | "mongodb"
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    filename = file.filename
    table_or_collection_name = os.path.splitext(filename)[0]

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif filename.endswith(".json"):
            df = pd.read_json(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Upload CSV or JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

    if database.lower() == "mysql":
        upload_to_mysql(df, table_or_collection_name)
    elif database.lower() == "mongodb":
        upload_to_mongodb(df, table_or_collection_name)
    else:
        raise HTTPException(status_code=400, detail="Invalid database type. Choose 'mysql' or 'mongodb'.")

    return {"message": "Dataset uploaded successfully!"}

def upload_to_mongodb(df: pd.DataFrame, collection_name: str):
    col = mongo_db[collection_name]
    data = df.to_dict(orient="records")
    if data:
        col.insert_many(data)

def upload_to_mysql(df: pd.DataFrame, table_name: str):
    mydb = get_mysql_connection()
    cursor = mydb.cursor()

    dtype_mapping = {
        'int64': 'INT',
        'float64': 'FLOAT',
        'object': 'VARCHAR(255)',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'DATETIME'
    }
    columns = ", ".join([f"`{col}` {dtype_mapping.get(str(dtype), 'VARCHAR(255)')}"
                         for col, dtype in df.dtypes.items()])
    create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns});"

    try:
        cursor.execute(create_table_query)
        for _, row in df.iterrows():
            placeholders = ", ".join(["%s"] * len(row))
            insert_query = f"INSERT INTO `{table_name}` VALUES ({placeholders})"
            cursor.execute(insert_query, tuple(row))
        mydb.commit()
    except mysql.connector.Error as err:
        mydb.rollback()
        raise HTTPException(status_code=500, detail=f"MySQL Error: {err}")
    finally:
        cursor.close()
        mydb.close()

# =========================
# MySQL: Explore
# =========================
@app.get("/mysql/tables")
def list_mysql_tables():
    mydb = get_mysql_connection()
    cursor = mydb.cursor()
    try:
        cursor.execute("SHOW TABLES;")
        tables = [t[0] for t in cursor.fetchall()]
        return {"tables": tables}
    finally:
        cursor.close()
        mydb.close()

@app.get("/mysql/table/{table_name}")
def describe_mysql_table(table_name: str):
    mydb = get_mysql_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute(f"DESCRIBE `{table_name}`;")
        columns = cursor.fetchall()

        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5;")
        sample_data = cursor.fetchall()

        for row in sample_data:
            for k, v in row.items():
                if isinstance(v, timedelta):
                    row[k] = str(v)
                elif isinstance(v, datetime):
                    row[k] = v.strftime("%Y-%m-%d %H:%M:%S")

        return {"columns": columns, "sample_data": sample_data}
    finally:
        cursor.close()
        mydb.close()

# =========================
# Mongo: Explore
# =========================
@app.get("/mongo/collections")
def list_mongo_collections():
    return {"collections": mongo_db.list_collection_names()}

@app.get("/mongo/collection/{collection_name}")
def describe_mongo_collection(collection_name: str):
    col = mongo_db[collection_name]
    sample = list(col.find().limit(5))
    for doc in sample:
        doc["_id"] = str(doc["_id"])
    sample = replace_nan_with_none(sample)
    return {"sample_data": sample}

# =========================
# Field Info Helpers (for sample queries)
# =========================
def get_mysql_field_info(table_name):
    mydb = get_mysql_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute(f"DESCRIBE `{table_name}`;")
        columns = cursor.fetchall()
    finally:
        cursor.close()
        mydb.close()

    mysql_to_general = {
        'int': 'int', 'tinyint': 'int', 'smallint': 'int', 'mediumint': 'int', 'bigint': 'int',
        'float': 'float', 'double': 'float', 'decimal': 'float',
        'varchar': 'string', 'text': 'string', 'char': 'string',
        'date': 'date', 'datetime': 'datetime', 'timestamp': 'datetime', 'time': 'time', 'year': 'int'
    }

    field_info = {}
    for column in columns:
        field_name = column['Field']
        field_type = re.sub(r'\(.*\)', '', column['Type']).lower()
        general_type = mysql_to_general.get(field_type, 'string')
        field_info[field_name] = general_type
    return field_info

def get_mongo_field_info(collection_name):
    col = mongo_db[collection_name]
    doc = col.find_one()
    bson_to_general = {int: 'int', float: 'float', str: 'string', list: 'array', dict: 'object', bool: 'boolean'}
    field_info = {}
    if doc:
        for k, v in doc.items():
            field_info[k] = bson_to_general.get(type(v), 'string')
    return field_info

# =========================
# Sample Query Generators (MySQL)
# =========================
@app.get("/mysql/sample-queries/{table_name}")
def get_mysql_sample_queries(table_name: str):
    fields = get_mysql_field_info(table_name)
    if not fields:
        raise HTTPException(status_code=404, detail=f"No fields found for table: {table_name}")

    quantitative = [f for f, t in fields.items() if t in ['int', 'float']]
    categorical = [f for f, t in fields.items() if t == 'string']

    patterns = [
        ("Total <A> by <B>", "SELECT {B}, SUM({A}) AS total_{A} FROM {table} GROUP BY {B};"),
        ("Average <A> by <B>", "SELECT {B}, AVG({A}) AS avg_{A} FROM {table} GROUP BY {B};"),
        ("Count of <A> by <B>", "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B};"),
        ("List of <A> ordered by <B>", "SELECT {A}, {B} FROM {table} ORDER BY {B} DESC LIMIT 10;")
    ]

    samples = []
    for desc, tpl in patterns:
        if quantitative and categorical:
            A = random.choice(quantitative)
            B = random.choice(categorical)
            q = tpl.replace("{A}", A).replace("{B}", B).replace("{table}", table_name)
            samples.append({"description": desc.replace("<A>", A).replace("<B>", B), "query": q})
    return {"queries": samples[:3]}

@app.get("/mysql/sample-queries/{table_name}/{construct}")
def get_mysql_sample_queries_with_construct(table_name: str, construct: str):
    fields = get_mysql_field_info(table_name)
    quantitative = [f for f, t in fields.items() if t in ['int', 'float']]
    categorical = [f for f, t in fields.items() if t == 'string']

    constructs = {
        "group_by": ("Count of <A> by <B>", "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B};"),
        "order_by": ("List <A> ordered by <B>", "SELECT {A}, {B} FROM {table} ORDER BY {B} DESC LIMIT 10;"),
        "having":   ("Group by <B> with count > 1", "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B} HAVING COUNT({A}) > 1;")
    }
    if construct not in constructs:
        raise HTTPException(status_code=400, detail=f"Unsupported construct: {construct}")

    desc_tpl, sql_tpl = constructs[construct]
    samples = []
    if quantitative and categorical:
        for _ in range(3):
            A = random.choice(quantitative); B = random.choice(categorical)
            q = sql_tpl.replace("{A}", A).replace("{B}", B).replace("{table}", table_name)
            samples.append({"description": desc_tpl.replace("<A>", A).replace("<B>", B), "query": q})
    return {"queries": samples}

# =========================
# Sample Query Generators (Mongo)
# =========================
@app.get("/mongo/sample-queries/{collection_name}")
def get_mongo_sample_queries(collection_name: str):
    fields = get_mongo_field_info(collection_name)
    quantitative = [f for f, t in fields.items() if t in ['int', 'float']]
    categorical = [f for f, t in fields.items() if t == 'string']

    patterns = [
        ("Total <A> by <B>",   "db.{collection}.aggregate([{{'$group': {{'_id': '${B}', 'total_{A}': {{'$sum': '${A}'}} }} }}])"),
        ("Average <A> by <B>", "db.{collection}.aggregate([{{'$group': {{'_id': '${B}', 'avg_{A}':   {{'$avg': '${A}'}} }} }}])"),
        ("Count of <A> by <B>","db.{collection}.aggregate([{{'$group': {{'_id': '${B}', 'count_{A}': {{'$sum': 1}} }} }}])"),
        ("List of <A> ordered by <B>", "db.{collection}.find({}, {{ {A}: 1, {B}: 1 }}).sort({{ {B}: -1 }}).limit(10)")
    ]

    samples = []
    for desc, tpl in patterns:
        if quantitative and categorical:
            A = random.choice(quantitative); B = random.choice(categorical)
            q = tpl.replace("{A}", A).replace("{B}", B).replace("{collection}", collection_name)
            samples.append({"description": desc.replace("<A>", A).replace("<B>", B), "query": q})
    return {"queries": samples[:3]}

@app.get("/mongo/sample-queries/{collection}/{construct}")
def get_mongo_sample_queries_with_construct(collection: str, construct: str):
    fields = get_mongo_field_info(collection)
    quantitative = [f for f, t in fields.items() if t in ['int', 'float']]
    categorical  = [f for f, t in fields.items() if t == 'string']

    constructs = {
        "group_by": ("Group by <B> and count <A>",
                     "db.{collection}.aggregate([{{'$group': {{'_id': '${B}', 'count_{A}': {{'$sum': 1}} }} }}])"),
        "order_by": ("List <A> ordered by <B>",
                     "db.{collection}.find({}, {{ {A}: 1, {B}: 1 }}).sort({{ {B}: -1 }}).limit(10)"),
        "having":   ("Group by <B> with count > 1",
                     "db.{collection}.aggregate([{{'$group': {{'_id': '${B}', 'count': {{'$sum': 1}} }} }}, {{'$match': {{'count': {{'$gt': 1}} }} }}])")
    }
    if construct not in constructs:
        raise HTTPException(status_code=400, detail=f"Unsupported construct: {construct}")

    desc_tpl, mongo_tpl = constructs[construct]
    samples = []
    if quantitative and categorical:
        for _ in range(3):
            A = random.choice(quantitative); B = random.choice(categorical)
            q = mongo_tpl.replace("{A}", A).replace("{B}", B).replace("{collection}", collection)
            samples.append({"description": desc_tpl.replace("<A>", A).replace("<B>", B), "query": q})
    return {"queries": samples}

# =========================
# Execute SQL (optional but handy)
# =========================
class SQLExecRequest(BaseModel):
    query: str = Field(..., min_length=1)

@app.post("/execute-query")
def execute_query(payload: SQLExecRequest):
    try:
        mydb = get_mysql_connection()
        cursor = mydb.cursor(dictionary=True)
        cursor.execute(payload.query)
        results = cursor.fetchall()
        cursor.close()
        mydb.close()

        for row in results:
            for k, v in row.items():
                if isinstance(v, timedelta):
                    row[k] = str(v)
                elif isinstance(v, datetime):
                    row[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        return {"results": results}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL Error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# =========================
# NLP → Query (kept compatible with your frontend)
# NOTE: This copies your pattern-matching approach.
# =========================
SQL_PATTERNS = [
    ("Total <A> by <B>", "SELECT {B}, SUM({A}) AS total_{A} FROM {table} GROUP BY {B};"),
    ("Average <A> by <B>", "SELECT {B}, AVG({A}) AS avg_{A} FROM {table} GROUP BY {B};"),
    ("Count of <A> by <B>", "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B};"),
    ("List of <A> ordered by <B>", "SELECT {A}, {B} FROM {table} ORDER BY {B} DESC LIMIT 10;")
]
MONGO_PATTERNS = [
    ("Total <A> by <B>",   "db.{collection}.aggregate([{{'$group': {{'_id': '${B}', 'total_{A}': {{'$sum': '${A}'}} }} }}])"),
    ("Average <A> by <B>", "db.{collection}.aggregate([{{'$group': {{'_id': '${B}', 'avg_{A}':   {{'$avg': '${A}'}} }} }}])"),
    ("Count of <A> by <B>","db.{collection}.aggregate([{{'$group': {{'_id': '${B}', 'count_{A}': {{'$sum': 1}} }} }}])"),
    ("List of <A> ordered by <B>", "db.{collection}.find({}, {{ {A}: 1, {B}: 1 }}).sort({{ {B}: -1 }}).limit(10)")
]

def match_pattern(user_query, patterns):
    for description, template in patterns:
        regex = description.lower().replace('<a>', r'(\w+)').replace('<b>', r'(\w+)')
        m = re.search(regex, user_query.lower())
        if m:
            return template, m.groups()
    return None, None

class NLPQueryRequest(BaseModel):
    query: str
    database: constr(strip_whitespace=True)  # "mysql" | "mongodb"
    table_or_collection: str

@app.post("/nlp-query")
def handle_nlp_query(payload: NLPQueryRequest):
    user_query = payload.query
    db_type = payload.database.lower()
    t_or_c = payload.table_or_collection

    patterns = SQL_PATTERNS if db_type == "mysql" else MONGO_PATTERNS
    template, entities = match_pattern(user_query, patterns)

    if not template or not entities:
        raise HTTPException(status_code=400, detail="Unable to parse query. Try a supported pattern.")

    query = template.format(
        A=entities[0],
        B=entities[1],
        table=t_or_c if db_type == "mysql" else "",
        collection=t_or_c if db_type == "mongodb" else ""
    )

    try:
        if db_type == "mysql":
            mydb = get_mysql_connection()
            cursor = mydb.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close(); mydb.close()

            for row in results:
                for k, v in row.items():
                    if isinstance(v, timedelta):
                        row[k] = str(v)
                    elif isinstance(v, datetime):
                        row[k] = v.strftime("%Y-%m-%d %H:%M:%S")

            return {"query": query, "results": results}

        elif db_type == "mongodb":
            # WARNING: your original version eval'd strings. Keeping parity for now,
            # but consider replacing this with explicit pipeline builders.
            col = mongo_db[t_or_c]
            if "aggregate" in query:
                # very limited, controlled eval
                import ast
                inner = query.split("aggregate(", 1)[1].rsplit(")", 1)[0]
                # convert JS-like to Python dict where possible
                inner = inner.replace("'", '"').replace("$", "$")  # still rough; your templates are simple
                pipeline = ast.literal_eval(inner)
                results = list(col.aggregate(pipeline))
            elif "find" in query:
                import ast
                inner = query.split("find(", 1)[1].rsplit(")", 1)[0]
                parts = inner.split("),", 1) if "), " in inner else [inner]
                find_args = ast.literal_eval(f"[{parts[0]}]")  # [filter]
                if "sort" in query:
                    # run the actual operations sequentially
                    cursor = col.find(*find_args)
                    sort_field = query.split(".sort({", 1)[1].split(":", 1)[0].strip()
                    cursor = cursor.sort(sort_field, -1)
                    cursor = cursor.limit(10)
                    results = list(cursor)
                else:
                    results = list(col.find(*find_args).limit(10))
            else:
                raise HTTPException(status_code=400, detail="Unsupported MongoDB query pattern")

            for d in results:
                if "_id" in d:
                    d["_id"] = str(d["_id"])
            return {"query": query, "results": results}

        else:
            raise HTTPException(status_code=400, detail="Unknown database type.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
