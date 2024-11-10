// src/App.js
import './App.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatabaseExplorer from './components/DatabaseExplorer';
import FileUpload from './components/FileUpload';

function App() {
    const [tables, setTables] = useState([]);
    const [collections, setCollections] = useState([]);
    const [selectedTable, setSelectedTable] = useState(null);
    const [selectedCollection, setSelectedCollection] = useState(null);
    const [tableDetails, setTableDetails] = useState(null);
    const [collectionDetails, setCollectionDetails] = useState(null);
    const [sampleQueries, setSampleQueries] = useState([]);

    // Fetch MySQL tables
    const fetchTables = () => {
        axios.get('http://localhost:5001/mysql/tables')
            .then(response => setTables(response.data.tables))
            .catch(error => console.error('Error fetching tables:', error));
    };

    // Fetch MongoDB collections
    const fetchCollections = () => {
        axios.get('http://localhost:5001/mongo/collections')
            .then(response => setCollections(response.data.collections))
            .catch(error => console.error('Error fetching collections:', error));
    };

    // Fetch MySQL table details
    const fetchTableDetails = (tableName) => {
        axios.get(`http://localhost:5001/mysql/table/${tableName}`)
            .then(response => {
                setSelectedTable(tableName);
                setTableDetails(response.data);
                setSelectedCollection(null);
                setCollectionDetails(null);
                setSampleQueries([]); // Clear previous sample queries
            })
            .catch(error => console.error('Error fetching table details:', error));
    };

    // Fetch MongoDB collection details
    const fetchCollectionDetails = (collectionName) => {
        axios.get(`http://localhost:5001/mongo/collection/${collectionName}`)
            .then(response => {
                setSelectedCollection(collectionName);
                setCollectionDetails(response.data);
                setSelectedTable(null);
                setTableDetails(null);
                setSampleQueries([]); // Clear previous sample queries
            })
            .catch(error => console.error('Error fetching collection details:', error));
    };

    // Fetch sample queries for the selected table or collection
    const fetchSampleQueries = () => {
        const apiUrl = selectedTable 
            ? `http://localhost:5001/mysql/sample-queries/${selectedTable}` 
            : `http://localhost:5001/mongo/sample-queries/${selectedCollection}`;

        axios.get(apiUrl)
            .then(response => setSampleQueries(response.data.queries))
            .catch(error => console.error('Error fetching sample queries:', error));
    };

    // Initial load to fetch tables and collections
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
                selectedTable={selectedTable}
                selectedCollection={selectedCollection}
                tableDetails={tableDetails}
                collectionDetails={collectionDetails}
                sampleQueries={sampleQueries}
                onSelectTable={fetchTableDetails}
                onSelectCollection={fetchCollectionDetails}
                fetchSampleQueries={fetchSampleQueries}
            />
        </div>
    );
}

export default App;
