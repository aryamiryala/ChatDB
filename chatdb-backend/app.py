from flask import Flask, request, jsonify, redirect, url_for
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired
import random
import mysql.connector
from pymongo import MongoClient
import pandas as pd
from datetime import timedelta, datetime
from flask_cors import CORS
import os
import numpy as np
import random
import re
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize the Flask app and enable CORS
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Set limit to 100 MB
CORS(app, resources={r"/*": {"origins": "*"}})

# MongoDB Connection (kept as a persistent connection)
client = MongoClient('localhost', 27017)  # Connect to MongoDB on localhost
mongo_db = client['ChatDB']  # Use the ChatDB database

# Helper function to create a MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="dsci@551-Tuesday-Section",  # Replace with your MySQL password
        database="ChatDB"  # Your MySQL database name
    )


# Helper function to replace NaN values with None in a dictionary
def replace_nan_with_none(data):
    if isinstance(data, list):
        return [replace_nan_with_none(item) for item in data]
    elif isinstance(data, dict):
        return {key: replace_nan_with_none(value) for key, value in data.items()}
    elif isinstance(data, float) and np.isnan(data):
        return None
    else:
        return data

@app.route('/')
def index():
    return "Welcome to ChatDB!"

@app.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        print("No file part in the request")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return jsonify({"error": "No selected file"}), 400

    filename = file.filename
    table_or_collection_name = os.path.splitext(filename)[0]  # Extract file name without extension
    print("Received file:", filename)
    print("Table/Collection name:", table_or_collection_name)

    # Check the database parameter
    database_type = request.form.get('database')
    print("Database type:", database_type)

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith('.json'):
            df = pd.read_json(file)
        else:
            print("Unsupported file format")
            return jsonify({"error": "Unsupported file format. Upload a CSV or JSON file."}), 400
    except Exception as e:
        print("Error processing file:", str(e))
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

    # Further processing for uploading to MySQL or MongoDB
    if database_type == 'mysql':
        upload_to_mysql(df, table_or_collection_name)
    elif database_type == 'mongodb':
        upload_to_mongodb(df, table_or_collection_name)
    else:
        print("Invalid database type")
        return jsonify({"error": "Invalid database type. Choose 'mysql' or 'mongodb'."}), 400

    print("Dataset uploaded successfully!")
    return jsonify({"message": "Dataset uploaded successfully!"}), 200

# Function to upload data to MongoDB
def upload_to_mongodb(df, collection_name):
    collection = mongo_db[collection_name]
    data = df.to_dict(orient="records")
    collection.insert_many(data)

# Function to upload data to MySQL with inferred data types
def upload_to_mysql(df, table_name):
    # Establish a new connection for each upload
    mydb = get_mysql_connection()
    cursor = mydb.cursor()
    
    # Infer column types and map them to MySQL types
    dtype_mapping = {
        'int64': 'INT',
        'float64': 'FLOAT',
        'object': 'VARCHAR(255)',  # Treat text columns as VARCHAR
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'DATETIME'
    }
    
    # Build a CREATE TABLE statement with inferred types
    columns = ", ".join([f"`{col}` {dtype_mapping.get(str(dtype), 'VARCHAR(255)')}" 
                         for col, dtype in df.dtypes.items()])
    create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns});"
    
    try:
        cursor.execute(create_table_query)
        
        # Insert each row into the MySQL table
        for _, row in df.iterrows():
            placeholders = ", ".join(["%s"] * len(row))
            insert_query = f"INSERT INTO `{table_name}` VALUES ({placeholders})"
            cursor.execute(insert_query, tuple(row))

        mydb.commit()
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        mydb.rollback()  # Roll back if there's an error
    finally:
        cursor.close()
        mydb.close()  # Close connection after upload


# New routes for exploring MySQL and MongoDB databases

# MySQL Routes
@app.route('/mysql/tables', methods=['GET'])
def list_mysql_tables():
    mydb = get_mysql_connection()
    cursor = mydb.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [table[0] for table in cursor.fetchall()]
    cursor.close()
    mydb.close()
    return jsonify({"tables": tables})

@app.route('/mysql/table/<table_name>', methods=['GET'])
def describe_mysql_table(table_name):
    mydb = get_mysql_connection()
    cursor = mydb.cursor(dictionary=True)
    
    # Get column details
    cursor.execute(f"DESCRIBE `{table_name}`;")
    columns = cursor.fetchall()
    
    # Get sample data (limit to first 5 rows)
    cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5;")
    sample_data = cursor.fetchall()

    # Convert timedelta and datetime objects to strings
    for row in sample_data:
        for key, value in row.items():
            if isinstance(value, timedelta):
                row[key] = str(value)
            elif isinstance(value, datetime):
                row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.close()
    mydb.close()
    return jsonify({"columns": columns, "sample_data": sample_data})

# MongoDB Routes
@app.route('/mongo/collections', methods=['GET'])
def list_mongo_collections():
    collections = mongo_db.list_collection_names()
    return jsonify({"collections": collections})

@app.route('/mongo/collection/<collection_name>', methods=['GET'])
def describe_mongo_collection(collection_name):
    collection = mongo_db[collection_name]
    
    # Get sample documents (limit to first 5 documents)
    sample_data = list(collection.find().limit(5))
    for doc in sample_data:
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string for JSON compatibility

    # Replace NaN values with None
    sample_data = replace_nan_with_none(sample_data)
    
    return jsonify({"sample_data": sample_data})

# Helper function to get field information for a MySQL table
def get_mysql_field_info(table_name):
    mydb = get_mysql_connection()
    cursor = mydb.cursor(dictionary=True)
    
    # Get column information
    cursor.execute(f"DESCRIBE `{table_name}`;")
    columns = cursor.fetchall()
    cursor.close()
    mydb.close()

    # Map MySQL data types to general types
    mysql_to_general = {
        'int': 'int',
        'tinyint': 'int',
        'smallint': 'int',
        'mediumint': 'int',
        'bigint': 'int',
        'float': 'float',
        'double': 'float',
        'decimal': 'float',
        'varchar': 'string',
        'text': 'string',
        'char': 'string',
        'date': 'date',
        'datetime': 'datetime',
        'timestamp': 'datetime',
        'time': 'time',
        'year': 'int'
    }

    field_info = {}
    for column in columns:
        field_name = column['Field']
        field_type = re.sub(r'\(.*\)', '', column['Type']).lower()
        general_type = mysql_to_general.get(field_type, 'string')
        field_info[field_name] = general_type

    return field_info


# Helper function to get field information for a MongoDB collection
def get_mongo_field_info(collection_name):
    collection = mongo_db[collection_name]
    sample_document = collection.find_one()

    bson_to_general = {
        int: 'int',
        float: 'float',
        str: 'string',
        list: 'array',
        dict: 'object',
        bool: 'boolean'
    }

    field_info = {}
    if sample_document:
        for field, value in sample_document.items():
            field_type = type(value)
            general_type = bson_to_general.get(field_type, 'string')
            field_info[field] = general_type

    return field_info


@app.route('/mysql/sample-queries/<table_name>', methods=['GET'])
def get_mysql_sample_queries(table_name):
    fields = get_mysql_field_info(table_name)

    if not fields:
        return jsonify({"error": f"No fields found for table: {table_name}"}), 404

    # Separate fields into quantitative and categorical based on inferred types
    quantitative_fields = [field for field, field_type in fields.items() if field_type in ['int', 'float']]
    categorical_fields = [field for field, field_type in fields.items() if field_type == 'string']

    # Define query patterns with placeholders {A} and {B}
    query_patterns = [
        ("Total <A> by <B>", "SELECT {B}, SUM({A}) AS total_{A} FROM {table} GROUP BY {B};"),
        ("Average <A> by <B>", "SELECT {B}, AVG({A}) AS avg_{A} FROM {table} GROUP BY {B};"),
        ("Count of <A> by <B>", "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B};"),
        ("List of <A> ordered by <B>", "SELECT {A}, {B} FROM {table} ORDER BY {B} DESC LIMIT 10;")
    ]

    # Generate sample queries by replacing placeholders
    sample_queries = []
    for description, pattern in query_patterns:
        if quantitative_fields and categorical_fields:
            A = random.choice(quantitative_fields)
            B = random.choice(categorical_fields)
            query = (
                pattern.replace("{A}", A)
                       .replace("{B}", B)
                       .replace("{table}", table_name)
            )
            sample_queries.append({"description": description.replace("<A>", A).replace("<B>", B), "query": query})

    return jsonify({"queries": sample_queries[:3]})


@app.route('/mysql/sample-queries/<table_name>/<construct>', methods=['GET'])
def get_mysql_sample_queries_with_construct(table_name, construct):
    print(f"Received request for table: {table_name}")
    fields = get_mysql_field_info(table_name)

    # Separate fields into quantitative and categorical based on inferred types
    quantitative_fields = [field for field, field_type in fields.items() if field_type in ['int', 'float']]
    categorical_fields = [field for field, field_type in fields.items() if field_type == 'string']

    # Define construct-based query templates
    construct_query_patterns = {
        "group_by": ("Count of <A> by <B>",
                     "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B};"),
        "order_by": ("List <A> ordered by <B>",
                     "SELECT {A}, {B} FROM {table} ORDER BY {B} DESC LIMIT 10;"),
        "having": ("Group by <B> with count > 1",
                   "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B} HAVING COUNT({A}) > 1;")
    }

    # Validate construct
    if construct not in construct_query_patterns:
        return jsonify({"error": f"Unsupported construct: {construct}"}), 400

    sample_queries = []

    # Generate construct queries (group_by, order_by, having)
    if quantitative_fields and categorical_fields:
        for _ in range(3):
            A = random.choice(quantitative_fields)
            B = random.choice(categorical_fields)
            description_template, query_template = construct_query_patterns[construct]
            query = (
                query_template.replace("{A}", A)
                              .replace("{B}", B)
                              .replace("{table}", table_name)
            )
            description = description_template.replace("<A>", A).replace("<B>", B)
            sample_queries.append({"description": description, "query": query})

    return jsonify({"queries": sample_queries})



@app.route('/mongo/sample-queries/<collection_name>', methods=['GET'])
def get_mongo_sample_queries(collection_name):
    fields = get_mongo_field_info(collection_name)

    # Separate fields into quantitative and categorical based on inferred types
    quantitative_fields = [field for field, field_type in fields.items() if field_type in ['int', 'float']]
    categorical_fields = [field for field, field_type in fields.items() if field_type == 'string']
    
    # Define query patterns with placeholders {A} and {B}
    query_patterns = [
        ("Total <A> by <B>", "db.{collection}.aggregate([{{ '$group': {{ '_id': '${B}', 'total_{A}': {{ '$sum': '${A}' }} }} }}])"),
        ("Average <A> by <B>", "db.{collection}.aggregate([{{ '$group': {{ '_id': '${B}', 'avg_{A}': {{ '$avg': '${A}' }} }} }}])"),
        ("Count of <A> by <B>", "db.{collection}.aggregate([{{ '$group': {{ '_id': '${B}', 'count_{A}': {{ '$sum': 1 }} }} }}])"),
        ("List of <A> ordered by <B>", "db.{collection}.find({}, {{ {A}: 1, {B}: 1 }}).sort({{ {B}: -1 }}).limit(10)")
    ]

    # Generate sample queries by replacing placeholders
    sample_queries = []
    for description, pattern in query_patterns:
        if quantitative_fields and categorical_fields:
            A = random.choice(quantitative_fields)
            B = random.choice(categorical_fields)
            query = (
                pattern.replace("{A}", A)
                       .replace("{B}", B)
                       .replace("{collection}", collection_name)
            )
            sample_queries.append({"description": description.replace("<A>", A).replace("<B>", B), "query": query})

    return jsonify({"queries": sample_queries[:3]})


@app.route('/mongo/sample-queries/<collection>/<construct>', methods=['GET'])
def get_mongo_sample_queries_with_construct(collection, construct):
    fields = get_mongo_field_info(collection)

    # Separate fields into quantitative and categorical based on inferred types
    quantitative_fields = [field for field, field_type in fields.items() if field_type in ['int', 'float']]
    categorical_fields = [field for field, field_type in fields.items() if field_type == 'string']

    # Define construct-based query templates
    construct_query_patterns = {
        "group_by": ("Group by <B> and count <A>",
                     "db.{collection}.aggregate([{{ '$group': {{ '_id': '${B}', 'count_{A}': {{ '$sum': 1 }} }} }}])"),
        "order_by": ("List <A> ordered by <B>",
                     "db.{collection}.find({}, {{ {A}: 1, {B}: 1 }}).sort({{ {B}: -1 }}).limit(10)"),
        "having": ("Group by <B> with count > 1",
                   "db.{collection}.aggregate([{{ '$group': {{ '_id': '${B}', 'count': {{ '$sum': 1 }} }} }}, {{ '$match': {{ 'count': {{ '$gt': 1 }} }} }}])")
    }

    # Validate construct
    if construct not in construct_query_patterns:
        return jsonify({"error": f"Unsupported construct: {construct}"}), 400

    sample_queries = []

    # Generate construct queries (group_by, order_by, having)
    if quantitative_fields and categorical_fields:
        for _ in range(3):  
            A = random.choice(quantitative_fields)
            B = random.choice(categorical_fields)
            description_template, query_template = construct_query_patterns[construct]
            query = (
                query_template.replace("{A}", A)
                              .replace("{B}", B)
                              .replace("{collection}", collection)
            )
            description = description_template.replace("<A>", A).replace("<B>", B)
            sample_queries.append({"description": description, "query": query})

    return jsonify({"queries": sample_queries})


@app.route('/execute-query', methods=['POST'])
def execute_query():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Establish a new MySQL connection
        mydb = get_mysql_connection()
        cursor = mydb.cursor(dictionary=True)

        # Execute the user's query
        cursor.execute(user_query)
        results = cursor.fetchall()

        cursor.close()
        mydb.close()

        # Convert timedelta and datetime objects to strings for JSON serialization
        for row in results:
            for key, value in row.items():
                if isinstance(value, timedelta):
                    row[key] = str(value)
                elif isinstance(value, datetime):
                    row[key] = value.strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({"results": results})

    except mysql.connector.Error as err:
        return jsonify({"error": f"MySQL Error: {err}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Define SQL query patterns
SQL_PATTERNS = [
    ("Total <A> by <B>", "SELECT {B}, SUM({A}) AS total_{A} FROM {table} GROUP BY {B};"),
    ("Average <A> by <B>", "SELECT {B}, AVG({A}) AS avg_{A} FROM {table} GROUP BY {B};"),
    ("Count of <A> by <B>", "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B};"),
    ("List of <A> ordered by <B>", "SELECT {A}, {B} FROM {table} ORDER BY {B} DESC LIMIT 10;")
]


# Define MongoDB query patterns
MONGO_PATTERNS = [
    ("Total <A> by <B>", "db.{collection}.aggregate([{{ '$group': {{ '_id': '${B}', 'total_{A}': {{ '$sum': '${A}' }} }} }}])"),
    ("Average <A> by <B>", "db.{collection}.aggregate([{{ '$group': {{ '_id': '${B}', 'avg_{A}': {{ '$avg': '${A}' }} }} }}])"),
    ("Count of <A> by <B>", "db.{collection}.aggregate([{{ '$group': {{ '_id': '${B}', 'count_{A}': {{ '$sum': 1 }} }} }}])"),
    ("List of <A> ordered by <B>", "db.{collection}.find({}, {{ {A}: 1, {B}: 1 }}).sort({{ {B}: -1 }}).limit(10)")
]

def match_pattern(user_query, patterns):
    """Match the user query to a predefined pattern and generate the query"""
    for description, template in patterns:
        # Convert description to a regex pattern and find matches
        # Generate the regex pattern separately
        regex_pattern = description.lower().replace('<a>', r'(\w+)').replace('<b>', r'(\w+)')
        match = re.search(regex_pattern, user_query.lower())

        if match:
            return template, match.groups()
    return None, None


@app.route('/nlp-query', methods=['POST'])
def handle_nlp_query():
    """Handle NLP queries to generate SQL or MongoDB queries"""
    data = request.json
    user_query = data.get("query")
    db_type = data.get("database")
    table_or_collection = data.get("table_or_collection")

    if not user_query or not db_type or not table_or_collection:
        return jsonify({"error": "Query, database, and table/collection must be provided"}), 400

    # Match patterns based on database type
    patterns = SQL_PATTERNS if db_type == "mysql" else MONGO_PATTERNS
    template, entities = match_pattern(user_query, patterns)

    if not template or not entities:
        return jsonify({"error": "Unable to parse query. Please try again with a supported pattern."}), 400

    # Substitute entities into the template
    query = template.format(
        A=entities[0],
        B=entities[1],
        table=table_or_collection if db_type == "mysql" else "",
        collection=table_or_collection if db_type == "mongodb" else ""
    )

    return jsonify({"query": query})



if __name__ == '__main__':
    app.run(port=5001, debug=True)
