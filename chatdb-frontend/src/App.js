// src/App.js
import './App.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatabaseExplorer from './components/DatabaseExplorer';
import FileUpload from './components/FileUpload';

function App() {
    const [tables, setTables] = useState([]);
    const [collections, setCollections] = useState([]);

    const fetchTables = () => {
        axios.get('http://localhost:5001/mysql/tables')
            .then(response => setTables(response.data.tables))
            .catch(error => console.error('Error fetching tables:', error));
    };

    const fetchCollections = () => {
        axios.get('http://localhost:5001/mongo/collections')
            .then(response => setCollections(response.data.collections))
            .catch(error => console.error('Error fetching collections:', error));
    };

    useEffect(() => {
        fetchTables();
        fetchCollections();
    }, []);

    return (
        <div className="App">
            <h1>Welcome to ChatDB</h1>
            <div className="upload-section">
                <FileUpload fetchTables={fetchTables} fetchCollections={fetchCollections} />
            </div>
            <DatabaseExplorer
                tables={tables}
                collections={collections}
                fetchTables={fetchTables}
                fetchCollections={fetchCollections}
            />
        </div>
    );
}

export default App;
