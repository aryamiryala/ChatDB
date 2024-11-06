// src/App.js
import React from 'react';
import FileUpload from './components/FileUpload';
import DatabaseExplorer from './components/DatabaseExplorer';

function App() {
    return (
        <div className="App">
            <h1>Welcome to ChatDB</h1>
            <FileUpload />
            <DatabaseExplorer />
        </div>
    );
}

export default App;
