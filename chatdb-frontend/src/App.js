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
    const [constructQueries, setConstructQueries] = useState([]);

    
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
        
        console.log('Selected Table:', selectedTable);  // Log for debugging
        console.log('API URL:', apiUrl);               // Log for debugging
    
        axios.get(apiUrl)
        .then(response => {
            setSampleQueries(response.data.queries);
        })
        .catch(error => {
            // Log detailed error information
            console.error('Error fetching sample queries:', error.toJSON());
            alert('Failed to fetch sample queries. Check API configuration.');
        });
};

    // Fetch sample queries with constructs for the selected table or collection
    const fetchConstructBasedQueries = (construct) => {
        if (!selectedTable && !selectedCollection) {
            console.error('No table or collection selected for construct-based queries');
            return;
        }
    
        const apiUrl = selectedTable
            ? `http://localhost:5001/mysql/sample-queries/${selectedTable}/${construct}`
            : `http://localhost:5001/mongo/sample-queries/${selectedCollection}/${construct}`;
    
        axios
            .get(apiUrl)
            .then((response) => {
                setConstructQueries(response.data.queries || []);
            })
            .catch((error) => {
                console.error('Error fetching construct-based queries:', error);
                setConstructQueries([]); // Reset queries in case of an error
            });
    };

    // NLP Query Handling
    const handleNLPQuery = (queryInput) => {
        if (!queryInput.trim()) {
            alert("Please enter a query.");
            return;
        }

        const payload = {
            query: queryInput,
            database: selectedTable ? "mysql" : "mongodb",
            table_or_collection: selectedTable || selectedCollection,
        };

        axios.post("http://localhost:5001/nlp-query", payload)
            .then(response => {
                const { query } = response.data;
                alert(`Generated Query:\n${query}`);
            })
            .catch(error => {
                console.error("Error processing query:", error);
                alert("Failed to process the query. Check your input and try again.");
            });
    };

    

    // Initial load to fetch tables and collections
    useEffect(() => {
        fetchTables();
        fetchCollections();
    }, []);

    return (
        <div className="App">
            <h1>Welcome to ChatDB</h1>
            <p>Your intelligent database companion</p>
    <div className="upload-section">
        <FileUpload 
            fetchTables={fetchTables} 
            fetchCollections={fetchCollections} 
            buttonClass="upload-button" /* Pass the className for the button */
        />
            </div>
            <DatabaseExplorer
                tables={tables}
                collections={collections}
                selectedTable={selectedTable}
                selectedCollection={selectedCollection}
                tableDetails={tableDetails}
                collectionDetails={collectionDetails}
                sampleQueries={sampleQueries}
                constructQueries={constructQueries}
                setConstructQueries={setConstructQueries}
                onSelectTable={fetchTableDetails}
                onSelectCollection={fetchCollectionDetails}
                fetchSampleQueries={fetchSampleQueries}
                fetchConstructBasedQueries={fetchConstructBasedQueries} 
                handleNLPQuery={handleNLPQuery}
            />
        </div>
    );
}

export default App;