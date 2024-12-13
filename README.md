# ChatDB

## Overview

ChatDB is an intelligent database companion that provides an easy interface for querying both MySQL and MongoDB databases. It generates sample queries, allows for querying through natural language, and offers insights into database tables and collections. ChatDB features a frontend built with React and a backend powered by Flask, facilitating communication between the user and databases.

## File Structure

### Frontend

The frontend is a React-based application that serves as the user interface. It provides features to explore databases, upload datasets, and execute SQL or NoSQL queries.

- **`frontend/src/App.js`**: Main React component that manages the app state, including fetching tables/collections, displaying details, and managing query execution. It interfaces with the backend to fetch and display results.
- **`frontend/src/components/DatabaseExplorer.js`**: Handles the database exploration UI, allowing users to select tables or collections, view details, and interact with queries.
- **`frontend/src/components/FileUpload.js`**: Handles file uploads, where users can upload CSV or JSON files to populate the MySQL or MongoDB databases.
- **`frontend/src/App.css`**: Contains styles for the frontend components, including layout, colors, and interactive elements.

### Backend

The backend is powered by Flask and communicates with both MySQL and MongoDB databases. It processes natural language queries, handles database exploration, and generates SQL/NoSQL queries.

- **`backend/app.py`**: Main backend file that contains the API routes and logic for interacting with MySQL and MongoDB. It includes endpoints for uploading datasets, querying databases, and generating SQL/NoSQL queries.


### Prerequisites

Ensure you have the following installed:
- **Node.js** (for frontend)
- **Python 3.x** (for backend)
- **MySQL** and **MongoDB** running locally or remotely


## Running the Project


Before running the project, it's recommended to set up a Python virtual environment to manage dependencies.

    1) In the ChatDB folder create a virtual environment: python3 -m venv venv
    2) Activate it by doing: source venv/bin/activate (mac), venv\Scripts\activate(windows)
    3) Install required dependencies: pip install -r requirements.txt






To run frontend: 

    1) Naviagate to the chatdb-frontend folder
    2) Install required dependencies by doing npm install 
    3) Start the frontend development server by doing npm start
    4) The frontend will be available at http://localhost:3000 

To run backend: 
    1) Naviagate to the chatdb-backend folder
    2) Make sure your python virtual environment is on
    3) Start the Flask backend server by doing python3 app.py
    4) The backend will be available at http://localhost:5001

### Features

**Database Exploration**: Allows users to browse MySQL tables and MongoDB collections, view their structure, and fetch sample data.  
**File Upload**: Users can upload CSV or JSON files to populate either MySQL or MongoDB.  
**Sample Queries**: Users can request sample queries for a selected table or collection, including query constructs like GROUP BY, ORDER BY, and HAVING.  
**Construct Queries**: Users can fetch queries based on specific constructs like GROUP BY or ORDER BY and view sample queries generated using these constructs.  
**Natural Language Querying**: Users can input natural language queries, which the backend processes to generate the corresponding SQL or MongoDB query and return results.
