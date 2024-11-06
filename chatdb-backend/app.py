from flask import Flask, request, jsonify
import mysql.connector
from pymongo import MongoClient
import pandas as pd
from datetime import timedelta, datetime
from flask_cors import CORS
import os

# Initialize the Flask app and enable CORS
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Set limit to 100 MB
CORS(app, origins="http://localhost:3000")

# MySQL Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="dsci@551-Tuesday-Section",  # Replace with your MySQL password
    database="ChatDB"  # Your MySQL database name
)

# MongoDB Connection
client = MongoClient('localhost', 27017)  # Connect to MongoDB on localhost
mongo_db = client['ChatDB']  # Use the ChatDB database

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

# Function to upload data to mySQL
def upload_to_mysql(df, table_name):
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


# MySQL Route for Sales Data
@app.route('/mysql-sales', methods=['GET'])
def get_mysql_sales():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sales LIMIT 10;")
    result = cursor.fetchall()

    # Convert timedelta and other non-serializable objects to string
    for row in result:
        for key, value in row.items():
            if isinstance(value, timedelta):  # Convert timedelta to string
                row[key] = str(value)
            if isinstance(value, datetime):  # Convert datetime to string
                row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify(result)

# MongoDB Route for Sales Data
@app.route('/mongo-sales', methods=['GET'])
def get_mongo_sales():
    sales = mongo_db.sales.find().limit(10)
    result = []
    for sale in sales:
        sale['_id'] = str(sale['_id'])  # Convert ObjectId to string for JSON
        result.append(sale)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
