import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

function StatusPage() {
  const [inputFileName, setInputFileName] = useState('');
  const [searchParams] = useSearchParams();
  const [fileParam, setFileParam] = useState(searchParams.get('file'));
  const [status, setStatus] = useState('LOADING');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!fileParam) {
      setError('No file parameter found in URL.');
      return;
    }

    const checkStatus = async () => {
      try {
        const response = await fetch(`/queue/status/${fileParam}`);
        if (!response.ok) {
          setStatus('ERROR');
          return;
        }

        const data = await response.json();
        setStatus(data.status);
      } catch (err) {
        console.error(err);
        setStatus('ERROR');
      }
    };

    checkStatus();
    const interval = setInterval(() => {
      checkStatus();
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, [fileParam]);

  const getStatusMessage = () => {
    switch (status) {
      case 'PROCESSED':
        return 'Your file has been processed. You can download it below!';
      case 'PROCESSING':
        return 'Your file is currently processing...';
      case 'QUEUED':
        return 'Your file is in the queue. Please wait.';
      case 'ERROR':
        return 'An error occurred.';
      case 'NOTFOUND':
        return 'File not found.';
      default:
        return 'Loading...';
    }
  };

  const handleInputFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.value) {
      e.target.value = e.target.value.replace("\n", "");
      setInputFileName(e.target.value);
    }
  };

  const handleSwitchStatus = () => {
    setFileParam(inputFileName);
    setError('')
  };
  

  return (
    <div className="container">
      <h1>Video File Status</h1>
      {error && (
        <>
          <p style={{ color: '#ff6666' }}>{error}</p>
          <div style={{ marginTop:"1rem" }}>
            <label htmlFor="file">Enter the video filename you want to check the status of:</label>
            <input id="inputFileName" type="text" onChange={handleInputFileChange} placeholder="Enter filename..."></input>
            <div style={{ marginTop: '1rem' }}>
              <button onClick={handleSwitchStatus}>View File Status</button>
            </div>
          </div>
        </>
      )}
      {!error && (
        <>
          <p>
            Feel free to save the URL and/or filename to check the status again at any time!
          </p>
          <p>
            If you feel like your video is taking especially long to process, it's likely that
            either your video has a large number of frames, the neural network processor is in the
            middle of training, or the neural network processor is down altogether.
          </p>
          <p>
            Checking status for:
            <strong> {fileParam}</strong>
          </p>
          <h2>{getStatusMessage()}</h2>
          {status === 'PROCESSED' && (
            <a
              href={`/queue/download/${fileParam}`}
              style={{ marginTop: '1rem', display: 'inline-block' }}
            >
              <button>Download Processed File</button>
            </a>
          )}
        </>
      )}
    </div>
  );
}

export default StatusPage;