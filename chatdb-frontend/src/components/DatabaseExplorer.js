import React, { useState } from "react";

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
  onSubmitQuery
}) => {
  const [selectedTab, setSelectedTab] = useState("editor");
  const [queryInput, setQueryInput] = useState("");

  const handleSubmitQuery = () => {
    if (onSubmitQuery) onSubmitQuery(queryInput);
  };

  return (
    <div className="explorer-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <h2 className="sidebar-title">Database Explorer</h2>
        
        <div className="sidebar-section">
          <h3 className="section-header">MySQL Tables</h3>
          <ul className="table-list">
            {tables.map((table) => (
              <li
                key={table}
                onClick={() => onSelectTable(table)}
                className={`table-item ${selectedTable === table ? "selected" : ""}`}
              >
                {table}
              </li>
            ))}
          </ul>
        </div>

        <div className="sidebar-section">
          <h3 className="section-header">MongoDB Collections</h3>
          <ul className="table-list">
            {collections.map((collection) => (
              <li
                key={collection}
                onClick={() => onSelectCollection(collection)}
                className={`table-item ${selectedCollection === collection ? "selected" : ""}`}
              >
                {collection}
              </li>
            ))}
          </ul>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Query Interface */}
        <div className="query-interface">
          <div className="tab-list">
            <button 
              className={`tab-btn ${selectedTab === "editor" ? "active" : ""}`}
              onClick={() => setSelectedTab("editor")}
            >
              <span className="icon">⟨⟩</span> Query Editor
            </button>
            <button 
              className={`tab-btn ${selectedTab === "details" ? "active" : ""}`}
              onClick={() => setSelectedTab("details")}
            >
              <span className="icon">□</span> Table Details
            </button>
            <button 
              className={`tab-btn ${selectedTab === "sample" ? "active" : ""}`}
              onClick={() => setSelectedTab("sample")}
            >
              <span className="icon">≡</span> Sample Queries
            </button>
            <button 
              className={`tab-btn ${selectedTab === "builder" ? "active" : ""}`}
              onClick={() => setSelectedTab("builder")}
            >
              <span className="icon">⚙</span> Query Constructor
            </button>
          </div>

          {selectedTab === "editor" && (
            <div className="query-editor-card">
              <textarea 
                className="query-input"
                placeholder="Ask a question about your data.."
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
              />
              <button 
                className="submit-query-btn"
                onClick={handleSubmitQuery}
              >
                🔍 Run Search
              </button>
            </div>
          )}

          {selectedTab === "details" && tableDetails && (
            <div className="details-card">
              <h3>Table Details</h3>
              <pre>{JSON.stringify(tableDetails, null, 2)}</pre>
            </div>
          )}

          {selectedTab === "sample" && (
            <div className="sample-queries-card">
              <button 
                className="primary-button"
                onClick={fetchSampleQueries}
              >
                Get Sample Queries
              </button>
              {sampleQueries.length > 0 && (
                <div className="queries-list">
                  {sampleQueries.map((query, index) => (
                    <div key={index} className="query-item">
                      <h4>{query.description}</h4>
                      <pre>{query.query}</pre>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {selectedTab === "builder" && (
            <div className="query-builder-card">
              <div className="button-group">
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
                <div className="queries-grid">
                  {constructQueries.map((query, index) => (
                    <div key={index} className="query-item">
                      <h4>{query.description}</h4>
                      <pre>{query.query}</pre>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-queries">No construct-based queries available</p>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DatabaseExplorer;