import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';
import Dashboard from './components/Dashboard/Dashboard';
import MemoryExplorer from './components/MemoryExplorer/MemoryExplorer';
import MemoryGraph from './components/MemoryGraph/MemoryGraph';
import InteractionHub from './components/Interaction/InteractionHub';
import FileViewer from './components/MemoryExplorer/FileViewer';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gray-900 text-gray-100">
        <Navbar />
        <main className="flex-grow container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/explore" element={<MemoryExplorer />} />
            <Route path="/explore/:path*" element={<FileViewer />} />
            <Route path="/graph" element={<MemoryGraph />} />
            <Route path="/interaction" element={<InteractionHub />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
