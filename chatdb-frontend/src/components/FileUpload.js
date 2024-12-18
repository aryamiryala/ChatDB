import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = ({ fetchTables, fetchCollections }) => {
    const [file, setFile] = useState(null);
    const [database, setDatabase] = useState('mysql');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleDatabaseChange = (e) => {
        setDatabase(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            alert("Please select a file first!");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("database", database);

        try {
            const response = await axios.post('http://localhost:5001/upload-dataset', formData);
            console.log("Response:", response);
            alert(response.data.message);

            if (database === 'mysql') {
                fetchTables();
            } else if (database === 'mongodb') {
                fetchCollections();
            }
        } catch (error) {
            console.error("Error uploading the file:", error);
            alert("File upload failed. Please try again.");
        }
    };

    return (
        <div className="upload-card">
            <div className="upload-row">
                <div className="upload-group">
                    <label>Select File:</label>
                    <div className="file-input">
                        <input
                            type="file"
                            id="file-upload"
                            onChange={handleFileChange}
                            style={{ display: 'none' }}
                        />
                        <button 
                            type="button"
                            className="choose-file-btn"
                            onClick={() => document.getElementById('file-upload').click()}
                        >
                            ↑ Choose File
                        </button>
                        <span className="file-name">
                            {file ? file.name : "No file chosen"}
                        </span>
                    </div>
                </div>

                <div className="upload-group">
                    <label>Select Database:</label>
                    <select 
                        className="database-select"
                        value={database}
                        onChange={handleDatabaseChange}
                    >
                        <option value="mysql">MySQL</option>
                        <option value="mongodb">MongoDB</option>
                    </select>
                </div>

                <button 
                    className="upload-dataset-btn"
                    onClick={handleSubmit}
                >
                    Upload Dataset
                </button>
            </div>
        </div>
    );
};

export default FileUpload;