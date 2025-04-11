import { Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import StatusPage from './pages/StatusPage';
import TopBar from './pages/components/TopBar'
import ContactPage from './pages/ContactPage';

function App() {
  return (
    <>
      <TopBar />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/status" element={<StatusPage />} />
        <Route path="/contact" element={<ContactPage />} />
      </Routes>
    </>
  );
}

export default App;