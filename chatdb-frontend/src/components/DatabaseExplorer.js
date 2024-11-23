import React, { useState, useEffect } from "react";

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
  const [isDataAvailable, setIsDataAvailable] = useState(false);

  // Watch tables and collections to enable sections when data is available
  useEffect(() => {
    setIsDataAvailable(tables.length > 0 || collections.length > 0);
  }, [tables, collections]);

  return (
    <div className="database-explorer">
      {/* Sidebar */}
      <aside className="sidebar">
        <h3>MySQL Tables</h3>
        <ul>
          {tables.map((table) => (
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
          {collections.map((collection) => (
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

      {/* Main Content */}
      <main className="main-content">
        <div className="content-container">
          {/* Table Details */}
          {selectedTable && tableDetails && (
            <div className="details-card">
              <h4>Table Details</h4>
              <pre>{JSON.stringify(tableDetails, null, 2)}</pre>
            </div>
          )}

          {/* Collection Details */}
          {selectedCollection && collectionDetails && (
            <div className="details-card">
              <h4>Collection Details for {selectedCollection}</h4>
              <pre>{JSON.stringify(collectionDetails, null, 2)}</pre>
            </div>
          )}

          {/* Sample Queries */}
          {isDataAvailable && (
            <div className="details-card">
            <h4>Sample Queries</h4>
              <button onClick={fetchSampleQueries}>Get Sample Queries</button>
              {sampleQueries.length > 0 && (
                <div>
                  <h4>Sample Queries</h4>
                  <ul>
                    {sampleQueries.map((queryObj, index) => (
                      <li key={index}>
                        <strong>{queryObj.description}</strong>
                        <pre>{queryObj.query}</pre>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Construct-Based Queries */}
          {isDataAvailable && (
            <div className="details-card">
              <h4>Construct-Based Queries</h4>
              <div className="construct-buttons">
                <button onClick={() => fetchConstructBasedQueries("group_by")}>
                  Group By
                </button>
                <button onClick={() => fetchConstructBasedQueries("order_by")}>
                  Order By
                </button>
                <button onClick={() => fetchConstructBasedQueries("having")}>
                  Having
                </button>
                <button onClick={() => fetchConstructBasedQueries("join")}>
                  Join
                </button>
              </div>
              {constructQueries.length > 0 ? (
                <ul>
                  {constructQueries.map((queryObj, index) => (
                    <li key={index}>
                      <strong>{queryObj.description}</strong>
                      <pre>{queryObj.query}</pre>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No construct-based queries available</p>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DatabaseExplorer;
