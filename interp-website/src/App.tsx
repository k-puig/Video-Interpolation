import { Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import StatusPage from './pages/StatusPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<UploadPage />} />
      <Route path="/status" element={<StatusPage />} />
    </Routes>
  );
}

export default App;