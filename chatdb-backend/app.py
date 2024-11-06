from flask import Flask, request, jsonify
import mysql.connector
from pymongo import MongoClient
import pandas as pd
from datetime import timedelta, datetime
from flask_cors import CORS
import os
import numpy as np

# Initialize the Flask app and enable CORS
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Set limit to 100 MB
CORS(app)

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

# Function to upload data to MySQL
def upload_to_mysql(df, table_name):
    # Establish a new connection for each upload
    mydb = get_mysql_connection()
    cursor = mydb.cursor()
    
    # Wrap column names in backticks to handle special characters
    columns = ", ".join([f"`{col}` VARCHAR(255)" for col in df.columns])
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
