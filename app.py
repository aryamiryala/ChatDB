from flask import Flask, jsonify
import mysql.connector
from pymongo import MongoClient
from datetime import timedelta, datetime

app = Flask(__name__)

# MySQL Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="dsci-551",  # Replace with your MySQL password
    database="coffee_shop"  # Your MySQL database name
)

# MongoDB Connection
client = MongoClient('localhost', 27017)  # Connect to MongoDB on localhost
mongo_db = client['coffee_shop']  # Use the coffee_shop database

@app.route('/')
def index():
    return "Welcome to ChatDB!"

# MySQL Route
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

# MongoDB Route
@app.route('/mongo-sales', methods=['GET'])
def get_mongo_sales():
    sales = mongo_db.sales.find().limit(10)
    result = []
    for sale in sales:
        sale['_id'] = str(sale['_id'])  # Convert ObjectId to string for JSON
        result.append(sale)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
