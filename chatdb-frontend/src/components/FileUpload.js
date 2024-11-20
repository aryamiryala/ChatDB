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

            // Immediately update the table or collection list after successful upload
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
        <div className="file-upload">
    <h2>Upload Dataset</h2>
    <form onSubmit={handleSubmit}>
        <div className="form-group">
            <label>Select File:</label>
            <label className="custom-file-label" htmlFor="file-input">Choose File</label>
            <input 
                type="file" 
                id="file-input" 
                onChange={handleFileChange} 
                className="file-input" 
            />
            {file && <span className="file-name">{file.name}</span>}
        </div>
        
        <div className="form-group">
            <label>Select Database:</label>
            <select value={database} onChange={handleDatabaseChange}>
                <option value="mysql">MySQL</option>
                <option value="mongodb">MongoDB</option>
            </select>
        </div>
        
        <button type="submit">Upload</button>
    </form>
</div>

    );
};

export default FileUpload;
