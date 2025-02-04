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
