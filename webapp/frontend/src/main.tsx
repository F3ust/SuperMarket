import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes, useParams } from 'react-router-dom';
import './index.css';
import Layout from './components/Layout';
import { ThemeProvider } from './components/ui';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import ModulePage from './pages/ModulePage';
import Deploy from './pages/Deploy';
import Simulator from './pages/Simulator';
import Explorer from './pages/Explorer';
import { DATA, MODULES, pathForSection } from './modules';

function NotFound() {
  return <div className="py-20 text-center"><h1 className="font-display text-2xl font-bold">Không tìm thấy trang</h1><a href="/" className="text-accent hover:underline">Về trang chủ</a></div>;
}
function OldChapter() {
  const { id = '' } = useParams();
  return <Navigate to={pathForSection(id)} replace />;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dieu-hanh" element={<Dashboard />} />
            {MODULES.map((m) => <Route key={m.id} path={m.path} element={<ModulePage key={m.id} m={m} />} />)}
            <Route path="/mo-phong" element={<Simulator />} />
            <Route path="/tra-cuu" element={<Explorer />} />
            <Route path="/trien-khai" element={<Deploy />} />
            <Route path="/du-lieu" element={<ModulePage m={DATA} />} />
            <Route path="/chuong/:id" element={<OldChapter />} />
            <Route path="/kham-pha" element={<Navigate to="/tra-cuu" replace />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
);
