// src/App.jsx
import React, { useState } from 'react';
import { Link, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import ScenePreview from './components/editor/ScenePreview';
import ExportButton from './components/ExportButton';
import ProjectHistory from './components/ProjectHistory';

// Exemplo de cenas para preview
const exampleScenes = [
  {
    texto: 'Bem-vindo ao editor!',
    imagens: ['/static/uploads/slides/project_1_arquivo1/slide_1_img_1.png'],
    background: '#f5f5f5',
  },
  {
    texto: 'Adicione seus slides e exporte!',
    imagens: [],
    background: '#e3f2fd',
  },
];

const App = () => {
  const [selectedScene, setSelectedScene] = useState(0);
  const projectId = 1; // Exemplo fixo, pode ser dinâmico

  return (
    <Router>
      <div style={{ minHeight: '100vh', background: '#f7f9fa' }}>
        <nav style={{ background: '#1976d2', color: '#fff', padding: 16, display: 'flex', gap: 24 }}>
          <Link to="/" style={{ color: '#fff', fontWeight: 600, textDecoration: 'none' }}>Editor</Link>
          <Link to="/historico" style={{ color: '#fff', fontWeight: 600, textDecoration: 'none' }}>Histórico</Link>
        </nav>
        <Routes>
          <Route path="/" element={
            <div style={{ maxWidth: 900, margin: '0 auto', padding: 24 }}>
              <h1>Editor de Vídeo</h1>
              <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
                <div style={{ flex: '1 1 320px', minWidth: 320 }}>
                  <h3>Preview da Cena</h3>
                  <ScenePreview scene={exampleScenes[selectedScene]} />
                  <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                    {exampleScenes.map((_, idx) => (
                      <button key={idx} onClick={() => setSelectedScene(idx)} style={{ padding: 4, borderRadius: 4, background: selectedScene === idx ? '#1976d2' : '#eee', color: selectedScene === idx ? '#fff' : '#333' }}>
                        {idx + 1}
                      </button>
                    ))}
                  </div>
                </div>
                <div style={{ flex: '1 1 320px', minWidth: 320 }}>
                  <h3>Exportação</h3>
                  <ExportButton projectId={projectId} />
                </div>
              </div>
            </div>
          } />
          <Route path="/historico" element={<ProjectHistory />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
