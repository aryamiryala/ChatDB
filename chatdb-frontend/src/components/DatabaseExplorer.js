// src/components/DatabaseExplorer.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUpload from './FileUpload'; // Make sure to import FileUpload

const DatabaseExplorer = () => {
    const [tables, setTables] = useState([]);
    const [collections, setCollections] = useState([]);
    const [selectedTable, setSelectedTable] = useState(null);
    const [selectedCollection, setSelectedCollection] = useState(null);
    const [tableDetails, setTableDetails] = useState(null);
    const [collectionDetails, setCollectionDetails] = useState(null);

    useEffect(() => {
        fetchTables();
        fetchCollections();
    }, []);

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

    const fetchTableDetails = (tableName) => {
        axios.get(`http://localhost:5001/mysql/table/${tableName}`)
            .then(response => {
                setSelectedTable(tableName);
                setTableDetails(response.data);
            })
            .catch(error => console.error('Error fetching table details:', error));
    };

    const fetchCollectionDetails = (collectionName) => {
        axios.get(`http://localhost:5001/mongo/collection/${collectionName}`)
            .then(response => {
                setSelectedCollection(collectionName);
                setCollectionDetails(response.data);
            })
            .catch(error => console.error('Error fetching collection details:', error));
    };

    return (
        <div>
            <h2>Database Explorer</h2>

            <FileUpload fetchTables={fetchTables} fetchCollections={fetchCollections} />

            <div>
                <h3>MySQL Tables</h3>
                <ul>
                    {tables.map(table => (
                        <li key={table} onClick={() => fetchTableDetails(table)}>
                            {table}
                        </li>
                    ))}
                </ul>

                {tableDetails && (
                    <div>
                        <h4>Table Details for {selectedTable}</h4>
                        <pre>{JSON.stringify(tableDetails, null, 2)}</pre>
                    </div>
                )}
            </div>

            <div>
                <h3>MongoDB Collections</h3>
                <ul>
                    {collections.map(collection => (
                        <li key={collection} onClick={() => fetchCollectionDetails(collection)}>
                            {collection}
                        </li>
                    ))}
                </ul>

                {collectionDetails && (
                    <div>
                        <h4>Collection Details for {selectedCollection}</h4>
                        <pre>{JSON.stringify(collectionDetails, null, 2)}</pre>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DatabaseExplorer;
