import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function UploadPage() {
  const [inputFileName, setInputFileName] = useState('');
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

  const handleInputFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.value) {
      e.target.value = e.target.value.replace("\n", "");
      setInputFileName(e.target.value);
    }
  };

  const handleSwitchToStatus = () => {
    navigate(`/status?file=${inputFileName}`)
  };

  return (
    <div className="container">
      <h1>Video Interpolator</h1>
      <p>
        Simply upload a video to double its framerate. For more information on what this service
        does, just check out our about page at the top.
      </p>

      <div style={{ marginTop:"2rem" }}>
        <label htmlFor="file">Select video file:</label>
        <input id="uploadFile" type="file" onChange={handleFileChange} />
        <div style={{ marginTop: '1rem' }}>
          <button onClick={handleUpload}>Upload New Video</button>
        </div>
      </div>

      <div style={{ marginTop:"2rem" }}>
        <label htmlFor="file">Or maybe you already have a video file you want to check:</label>
        <input id="inputFileName" type="text" onChange={handleInputFileChange} placeholder="Enter filename..."></input>
        <div style={{ marginTop: '1rem' }}>
          <button onClick={handleSwitchToStatus}>View File Status</button>
        </div>
      </div>

      {infoMessage && (
        <div style={{ marginTop: '1rem', color: '#fbfcfc' }}>{infoMessage}</div>
      )}

    </div>
  );
}

export default UploadPage;