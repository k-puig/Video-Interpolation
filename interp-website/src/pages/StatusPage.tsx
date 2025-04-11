import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

function StatusPage() {
  const [searchParams] = useSearchParams();
  const fileParam = searchParams.get('file');
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

  return (
    <div className="container">
      <h1>Video File Status</h1>
      {error && <p style={{ color: '#ff6666' }}>{error}</p>}
      {!error && (
        <>
          <p>
            Feel free to save the URL and check the status again at any time!
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