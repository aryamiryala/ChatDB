// src/App.js
import React from 'react';
import './App.css';
import DatabaseExplorer from './components/DatabaseExplorer';

function App() {
    return (
        <div className="App">
            <h1>Welcome to ChatDB</h1>
            <DatabaseExplorer />
        </div>
    );
}

export default App;
