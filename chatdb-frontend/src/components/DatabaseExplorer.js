// src/components/DatabaseExplorer.js
import React from 'react';

const DatabaseExplorer = ({
    tables,
    collections,
    fetchSampleQueries,
    fetchConstructBasedQueries,
    sampleQueries,
    constructQueries,
    onSelectTable,
    onSelectCollection,
    selectedTable,
    selectedCollection,
    tableDetails,
    collectionDetails,
}) => {
    return (
        <div className="database-explorer">
            <aside className="sidebar">
                <h3>MySQL Tables</h3>
                <ul>
                    {tables.map(table => (
                        <li
                            key={table}
                            onClick={() => onSelectTable(table)}
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
                            onClick={() => onSelectCollection(collection)}
                            className={selectedCollection === collection ? "selected" : ""}
                        >
                            {collection}
                        </li>
                    ))}
                </ul>
            </aside>

            <main className="main-content">
                <div className="content-container">
                    {/* Left Column: Table/Collection Details */}
                    <div className="details">
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
                    </div>

                    {/* Middle Column: Sample Queries */}
                    <div className="sample-queries">
                        {(selectedTable || selectedCollection) && (
                            <>
                                <button onClick={fetchSampleQueries}>Get Sample Queries</button>
                                {sampleQueries.length > 0 && (
                                    <div>
                                        <h4>Sample Queries</h4>
                                        <div className="sample-queries-content">
                                            <ul>
                                                {sampleQueries.map((queryObj, index) => (
                                                    <li key={index}>
                                                        <strong>{queryObj.description}</strong>
                                                        <pre>{queryObj.query}</pre>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>

                    {/* Right Column: Construct-Based Queries */}
                    <div className="construct-based-queries">
                        <h4>Construct-Based Queries</h4>
                        <div className="construct-buttons">
                            <button onClick={() => fetchConstructBasedQueries('group_by')}>Group By</button>
                            <button onClick={() => fetchConstructBasedQueries('order_by')}>Order By</button>
                            <button onClick={() => fetchConstructBasedQueries('having')}>Having</button>
                            <button onClick={() => fetchConstructBasedQueries('join')}>Join</button>
                        </div>
                        {constructQueries.length > 0 ? (
                            <div className="construct-queries-content">
                                <ul>
                                    {constructQueries.map((queryObj, index) => (
                                        <li key={index}>
                                            <strong>{queryObj.description}</strong>
                                            <pre>{JSON.stringify(queryObj.query, null, 2)}</pre>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ) : (
                            <p>No construct-based queries available</p>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};


export default DatabaseExplorer;
