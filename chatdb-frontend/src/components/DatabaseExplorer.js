// src/components/DatabaseExplorer.js
import React, { useState } from 'react';
import axios from 'axios';

const DatabaseExplorer = ({ tables, collections, fetchTables, fetchCollections }) => {
    const [selectedTable, setSelectedTable] = useState(null);
    const [selectedCollection, setSelectedCollection] = useState(null);
    const [tableDetails, setTableDetails] = useState(null);
    const [collectionDetails, setCollectionDetails] = useState(null);

    const fetchTableDetails = (tableName) => {
        axios.get(`http://localhost:5001/mysql/table/${tableName}`)
            .then(response => {
                setSelectedTable(tableName);
                setTableDetails(response.data);
                setSelectedCollection(null); // Clear any previous MongoDB selection
                setCollectionDetails(null);
            })
            .catch(error => console.error('Error fetching table details:', error));
    };

    const fetchCollectionDetails = (collectionName) => {
        axios.get(`http://localhost:5001/mongo/collection/${collectionName}`)
            .then(response => {
                setSelectedCollection(collectionName);
                setCollectionDetails(response.data);
                setSelectedTable(null); // Clear any previous MySQL selection
                setTableDetails(null);
            })
            .catch(error => console.error('Error fetching collection details:', error));
    };

    return (
        <div className="database-explorer">
            <aside className="sidebar">
                <h3>MySQL Tables</h3>
                <ul>
                    {tables.map(table => (
                        <li
                            key={table}
                            onClick={() => fetchTableDetails(table)}
                            className={selectedTable === table ? "selected" : ""}
                        >
                            {table}
                        </li>
                    ))}
                </ul>
                <h3>MongoDB Collections</h3>
                <ul>
                    {collections.map(collection => (
                        <li
                            key={collection}
                            onClick={() => fetchCollectionDetails(collection)}
                            className={selectedCollection === collection ? "selected" : ""}
                        >
                            {collection}
                        </li>
                    ))}
                </ul>
            </aside>

            <main className="main-content">
                {/* Display selected table or collection details here */}
                {selectedTable && tableDetails && (
                    <div>
                        <h4>Table Details for {selectedTable}</h4>
                        <pre>{JSON.stringify(tableDetails, null, 2)}</pre>
                    </div>
                )}

                {selectedCollection && collectionDetails && (
                    <div>
                        <h4>Collection Details for {selectedCollection}</h4>
                        <pre>{JSON.stringify(collectionDetails, null, 2)}</pre>
                    </div>
                )}
            </main>
        </div>
    );
};

export default DatabaseExplorer;
