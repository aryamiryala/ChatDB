# ChatDB

## Overview

**ChatDB** is an intelligent database companion designed to simplify querying and interacting with both **MySQL** and **MongoDB** databases. It enables users to generate sample queries, run queries through natural language input, and explore database tables and collections with ease. Built with a **React** frontend and a **Flask** backend, ChatDB facilitates smooth communication between users and the databases.

---

## File Structure

### **Frontend** (React-based)

The frontend serves as the user interface, providing features to explore databases, upload datasets, and execute SQL/NoSQL queries.

- **`frontend/src/App.js`**: The main React component that handles the app's state. It fetches tables/collections, displays their details, and manages query execution by interacting with the backend.
- **`frontend/src/components/DatabaseExplorer.js`**: Manages the UI for database exploration. Users can select tables or collections, view their details, and interact with queries.
- **`frontend/src/components/FileUpload.js`**: Handles file uploads, allowing users to upload CSV or JSON files to populate either MySQL or MongoDB databases.
- **`frontend/src/App.css`**: Contains the styles for frontend components, including layout, color schemes, and interactive elements.

### **Backend** (Flask-based)

The backend is powered by **Flask** and communicates with MySQL and MongoDB. It processes natural language queries, manages database exploration, and generates SQL/NoSQL queries.

- **`backend/app.py`**: The core backend file containing the API routes and logic for interacting with MySQL and MongoDB databases. This includes endpoints for uploading datasets, querying databases, and generating sample SQL/NoSQL queries.

---

## Prerequisites

Before running the project, make sure you have the following installed:

- **Node.js** (for the frontend)
- **Python 3.x** (for the backend)
- **MySQL** and **MongoDB** (running locally or remotely)

---


### Setting Up the Python Virtual Environment (for Backend)

1. In the **ChatDB** folder, create a virtual environment:
   ```bash
   python3 -m venv venv

2. Activate the virtual environment:

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

    
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt


## Running the Project

### To run the frontend:

1. Navigate to the **chatdb-frontend** folder:
   ```bash
   cd chatdb-frontend

2. Install the required dependencies:
    ```bash
   npm install

3. Start the frontend development server:
    ```bash
   npm start

4. The frontend will be available at http://localhost:3000

### To run the backend:

1. Navigate to the **chatdb-backend** folder:
   ```bash
   cd chatdb-backend

2. Make sure your Python virtual environment is activated (reference section above this on how to install and start it)

3. Start the Flask backend server:
    ```bash
   python3 app.py

4. The backend will be available at http://localhost:5001

## Features
**Database Exploration**: Allows users to browse MySQL tables and MongoDB collections, view their structure, and fetch sample data.  
**File Upload**: Users can upload CSV or JSON files to populate either MySQL or MongoDB.  
**Sample Queries**: Users can request sample queries for a selected table or collection, including query constructs like GROUP BY, ORDER BY, and HAVING.  
**Construct Queries**: Users can fetch queries based on specific constructs like GROUP BY or ORDER BY and view sample queries generated using these constructs.  
**Natural Language Querying**: Users can input natural language queries, which the backend processes to generate the corresponding SQL or MongoDB query and return results.

