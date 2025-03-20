<<<<<<< HEAD
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
=======
import { ChangeEvent, useRef, useState } from 'react';
import { saveAs } from 'file-saver';

function App() {
  const [file, setFile] = useState("");
  const inputFile = useRef(null);

  const upload = () => {
    inputFile.current?.click();
  }

  const onFileUpload = (event: ChangeEvent<HTMLInputElement>) => {
    event.stopPropagation();
    event.preventDefault();

    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setFile(file.name);
    fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData,
    }).then((res) => res.json().then((data) => {
      console.log(data);
    }));
  }

  const download = () => {
    fetch('http://localhost:5000/download/' + file).then((res) => res.blob().then((blob) => {
      saveAs(blob, file);
    }));
  }

  return (
    <>
      <h1>Video Interpolater</h1>
      <div className="card">
        <input type='file' id='file' ref={inputFile} style={{display: 'none'}} onChange={onFileUpload}></input>
        <button onClick={upload}>
          Upload Video
        </button>
        <p>
          Click above to upload a video to interpolate.
        </p>
        <button onClick={download}>Download File {file}</button>
      </div>
    </>
  );
}

export default App
>>>>>>> main
