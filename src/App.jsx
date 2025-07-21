// src/App.jsx
import React from 'react';
import AssetPanel from './components/AssetPanel';
import EditorCanvas from './components/editor/EditorCanvas';
import SceneList from './components/SceneList';
import Timeline from './components/Timeline';
import Toolbar from './components/Toolbar';
import './App.css';

/**
 * App: Componente principal que organiza o layout do editor.
 *
 * - Integra todos os componentes principais: Toolbar, AssetPanel,
 *   EditorCanvas, SceneList e Timeline.
 * - Define a estrutura visual da aplicação.
 */
function App() {
  return (
    <div className="app-container">
      <Toolbar />
      <div className="main-content">
        <AssetPanel />
        <EditorCanvas />
        <SceneList />
      </div>
      <Timeline />
    </div>
  );
}

export default App; 