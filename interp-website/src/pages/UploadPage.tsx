import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [infoMessage, setInfoMessage] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setInfoMessage('Please choose a file first.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('/queue/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        setInfoMessage('Failed to upload file.');
        return;
      }

      const data = await response.json();
      const uploadedFileName = data.fileName;
      setInfoMessage(`File uploaded successfully: ${uploadedFileName}`);

      navigate(`/status?file=${uploadedFileName}`);
    } catch (error) {
      console.error(error);
      setInfoMessage('An error occurred during file upload.');
    }
  };

  return (
    <div className="container">
      <h1>Video Interpolator</h1>
      <p>Simply upload a video to double its framerate.</p>
      <label htmlFor="file">Select video file:</label>
      <input type="file" id="file" onChange={handleFileChange} />
      
      <div style={{ marginTop: '1rem' }}>
        <button onClick={handleUpload}>Upload</button>
      </div>

      {infoMessage && (
        <p style={{ marginTop: '1rem', color: '#fbfcfc' }}>{infoMessage}</p>
      )}
    </div>
  );
}

export default UploadPage;