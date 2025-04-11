import { Route, Routes } from 'react-router-dom';
import AboutPage from './pages/AboutPage';
import TopBar from './pages/components/TopBar';
import ContactPage from './pages/ContactPage';
import StatusPage from './pages/StatusPage';
import UploadPage from './pages/UploadPage';

function App() {
  return (
    <>
      <TopBar />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/status" element={<StatusPage />} />
      </Routes>
    </>
  );
}

export default App;