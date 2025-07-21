#!/usr/bin/env python3
"""
Script de Correção Automática do Frontend - TecnoCursosAI
Corrige todos os problemas do React e implementa funcionalidades faltantes
"""

import os
import sys
import subprocess
import shutil
import time
import json
from pathlib import Path

class Colors:
    """Cores para output colorido"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_colored(text, color):
    """Imprimir texto colorido"""
    print(f"{color}{text}{Colors.ENDC}")

def print_header(text):
    """Imprimir cabeçalho"""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"  {text}", Colors.BOLD + Colors.WHITE)
    print_colored(f"{'='*60}", Colors.CYAN)

def check_node_installation():
    """Verificar se Node.js está instalado"""
    print_colored("🔍 Verificando Node.js...", Colors.BLUE)
    
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored(f"✅ Node.js encontrado: {result.stdout.strip()}", Colors.GREEN)
            return True
        else:
            print_colored("❌ Node.js não encontrado!", Colors.RED)
            return False
    except FileNotFoundError:
        print_colored("❌ Node.js não está instalado!", Colors.RED)
        return False

def check_npm_installation():
    """Verificar se NPM está instalado"""
    print_colored("🔍 Verificando NPM...", Colors.BLUE)
    
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print_colored(f"✅ NPM encontrado: {result.stdout.strip()}", Colors.GREEN)
            return True
        else:
            print_colored("❌ NPM não encontrado!", Colors.RED)
            return False
    except FileNotFoundError:
        print_colored("❌ NPM não está instalado!", Colors.RED)
        return False

def force_clean_node_modules():
    """Forçar limpeza do node_modules"""
    print_colored("🧹 Limpando node_modules...", Colors.BLUE)
    
    node_modules_path = Path("node_modules")
    if node_modules_path.exists():
        try:
            # Tentar remover arquivos individualmente
            for root, dirs, files in os.walk(node_modules_path, topdown=False):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except:
                        pass
                for dir in dirs:
                    try:
                        os.rmdir(os.path.join(root, dir))
                    except:
                        pass
            
            # Tentar remover o diretório principal
            try:
                shutil.rmtree(node_modules_path)
                print_colored("✅ node_modules removido com sucesso!", Colors.GREEN)
            except:
                print_colored("⚠️ Não foi possível remover completamente node_modules", Colors.YELLOW)
        except Exception as e:
            print_colored(f"⚠️ Erro ao limpar node_modules: {e}", Colors.YELLOW)
    else:
        print_colored("✅ node_modules não existe", Colors.GREEN)

def install_dependencies():
    """Instalar dependências do React"""
    print_colored("📦 Instalando dependências React...", Colors.BLUE)
    
    try:
        # Limpar cache do npm
        subprocess.run(["npm", "cache", "clean", "--force"], check=True, shell=True)
        
        # Instalar dependências
        result = subprocess.run(["npm", "install"], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print_colored("✅ Dependências instaladas com sucesso!", Colors.GREEN)
            return True
        else:
            print_colored(f"❌ Erro na instalação: {result.stderr}", Colors.RED)
            return False
    except Exception as e:
        print_colored(f"❌ Erro ao instalar dependências: {e}", Colors.RED)
        return False

def create_react_app_structure():
    """Criar estrutura completa do React App"""
    print_colored("🏗️ Criando estrutura React...", Colors.BLUE)
    
    # Criar diretórios necessários
    directories = [
        "src/components",
        "src/pages",
        "src/hooks",
        "src/utils",
        "src/services",
        "src/styles",
        "public"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Criar arquivo index.html
    index_html = """<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="TecnoCursos AI - Editor de Vídeos" />
    <title>TecnoCursos AI</title>
  </head>
  <body>
    <noscript>Você precisa habilitar JavaScript para executar este app.</noscript>
    <div id="root"></div>
  </body>
</html>"""
    
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    
    print_colored("✅ Estrutura React criada!", Colors.GREEN)

def create_main_app_component():
    """Criar componente principal do App"""
    print_colored("🎨 Criando componente principal...", Colors.BLUE)
    
    app_jsx = """import React, { useState, useEffect } from 'react';
import './App.css';
import AssetPanel from './components/AssetPanel';
import SceneList from './components/SceneList';
import Timeline from './components/Timeline';
import EditorCanvas from './components/EditorCanvas';
import Toolbar from './components/Toolbar';

function App() {
  const [currentProject, setCurrentProject] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [assets, setAssets] = useState([]);
  const [selectedScene, setSelectedScene] = useState(null);

  useEffect(() => {
    // Carregar projeto inicial
    loadInitialProject();
  }, []);

  const loadInitialProject = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/projects');
      const projects = await response.json();
      if (projects.length > 0) {
        setCurrentProject(projects[0]);
      }
    } catch (error) {
      console.error('Erro ao carregar projetos:', error);
    }
  };

  const handleAssetUpload = (newAsset) => {
    setAssets(prev => [...prev, newAsset]);
  };

  const handleSceneCreate = (newScene) => {
    setScenes(prev => [...prev, newScene]);
  };

  const handleSceneUpdate = (updatedScene) => {
    setScenes(prev => 
      prev.map(scene => 
        scene.id === updatedScene.id ? updatedScene : scene
      )
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>TecnoCursos AI - Editor de Vídeos</h1>
      </header>
      
      <div className="editor-container">
        <div className="sidebar">
          <AssetPanel 
            assets={assets}
            onAssetUpload={handleAssetUpload}
          />
          <SceneList 
            scenes={scenes}
            selectedScene={selectedScene}
            onSceneSelect={setSelectedScene}
            onSceneCreate={handleSceneCreate}
            onSceneUpdate={handleSceneUpdate}
          />
        </div>
        
        <div className="main-content">
          <Toolbar />
          <EditorCanvas 
            selectedScene={selectedScene}
            assets={assets}
          />
          <Timeline 
            scenes={scenes}
            onSceneUpdate={handleSceneUpdate}
          />
        </div>
      </div>
    </div>
  );
}

export default App;"""
    
    with open("src/App.jsx", "w", encoding="utf-8") as f:
        f.write(app_jsx)
    
    print_colored("✅ Componente principal criado!", Colors.GREEN)

def create_css_styles():
    """Criar estilos CSS"""
    print_colored("🎨 Criando estilos CSS...", Colors.BLUE)
    
    app_css = """/* TecnoCursos AI - Estilos Principais */

.App {
  text-align: center;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.App-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.editor-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background-color: #f5f5f5;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Componentes */
.component {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 10px;
  padding: 15px;
  background: white;
}

.component h3 {
  margin-top: 0;
  color: #333;
}

/* Botões */
.btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
}

.btn-secondary:hover {
  background-color: #545b62;
}

/* Formulários */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

/* Listas */
.list-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.3s;
}

.list-item:hover {
  background-color: #f8f9fa;
}

.list-item.selected {
  background-color: #e3f2fd;
  border-left: 3px solid #2196f3;
}

/* Timeline */
.timeline {
  height: 150px;
  background-color: #f8f9fa;
  border-top: 1px solid #ddd;
  padding: 10px;
  overflow-x: auto;
}

.timeline-track {
  height: 100%;
  background-color: white;
  border: 1px solid #ddd;
  position: relative;
}

/* Canvas */
.canvas-container {
  flex: 1;
  background-color: #f8f9fa;
  position: relative;
  overflow: hidden;
}

.canvas {
  width: 100%;
  height: 100%;
  background-color: white;
  border: 1px solid #ddd;
}

/* Responsividade */
@media (max-width: 768px) {
  .editor-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: 200px;
  }
}"""
    
    with open("src/App.css", "w", encoding="utf-8") as f:
        f.write(app_css)
    
    print_colored("✅ Estilos CSS criados!", Colors.GREEN)

def create_index_js():
    """Criar arquivo index.js"""
    print_colored("📄 Criando index.js...", Colors.BLUE)
    
    index_js = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
    
    with open("src/index.js", "w", encoding="utf-8") as f:
        f.write(index_js)
    
    print_colored("✅ index.js criado!", Colors.GREEN)

def create_index_css():
    """Criar index.css"""
    print_colored("🎨 Criando index.css...", Colors.BLUE)
    
    index_css = """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

* {
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow: hidden;
}"""
    
    with open("src/index.css", "w", encoding="utf-8") as f:
        f.write(index_css)
    
    print_colored("✅ index.css criado!", Colors.GREEN)

def create_component_files():
    """Criar arquivos de componentes"""
    print_colored("🧩 Criando componentes...", Colors.BLUE)
    
    components = {
        "AssetPanel.jsx": """import React, { useState } from 'react';

const AssetPanel = ({ assets, onAssetUpload }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setDragActive(true);
    }
  };

  const handleDragOut = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (files) => {
    Array.from(files).forEach(file => {
      const newAsset = {
        id: Date.now() + Math.random(),
        name: file.name,
        type: file.type,
        size: file.size,
        url: URL.createObjectURL(file)
      };
      onAssetUpload(newAsset);
    });
  };

  return (
    <div className="component">
      <h3>📁 Biblioteca de Assets</h3>
      
      <div 
        className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <p>Arraste arquivos aqui ou clique para selecionar</p>
        <input
          type="file"
          multiple
          onChange={(e) => handleFiles(e.target.files)}
          style={{ display: 'none' }}
          id="file-input"
        />
        <label htmlFor="file-input" className="btn">
          Selecionar Arquivos
        </label>
      </div>
      
      <div className="assets-list">
        {assets.map(asset => (
          <div key={asset.id} className="asset-item">
            <span>{asset.name}</span>
            <span className="asset-size">({Math.round(asset.size / 1024)}KB)</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AssetPanel;""",
        
        "SceneList.jsx": """import React, { useState } from 'react';

const SceneList = ({ scenes, selectedScene, onSceneSelect, onSceneCreate, onSceneUpdate }) => {
  const [newSceneName, setNewSceneName] = useState('');

  const handleCreateScene = () => {
    if (newSceneName.trim()) {
      const newScene = {
        id: Date.now(),
        name: newSceneName,
        duration: 5,
        elements: [],
        createdAt: new Date()
      };
      onSceneCreate(newScene);
      setNewSceneName('');
    }
  };

  const handleSceneDurationChange = (sceneId, duration) => {
    const updatedScene = scenes.find(s => s.id === sceneId);
    if (updatedScene) {
      onSceneUpdate({
        ...updatedScene,
        duration: parseInt(duration)
      });
    }
  };

  return (
    <div className="component">
      <h3>🎭 Lista de Cenas</h3>
      
      <div className="create-scene">
        <input
          type="text"
          value={newSceneName}
          onChange={(e) => setNewSceneName(e.target.value)}
          placeholder="Nome da nova cena"
          className="form-control"
        />
        <button onClick={handleCreateScene} className="btn">
          + Nova Cena
        </button>
      </div>
      
      <div className="scenes-list">
        {scenes.map(scene => (
          <div 
            key={scene.id} 
            className={`scene-item ${selectedScene?.id === scene.id ? 'selected' : ''}`}
            onClick={() => onSceneSelect(scene)}
          >
            <div className="scene-header">
              <span className="scene-name">{scene.name}</span>
              <span className="scene-duration">{scene.duration}s</span>
            </div>
            <div className="scene-controls">
              <label>Duração:</label>
              <input
                type="number"
                min="1"
                max="60"
                value={scene.duration}
                onChange={(e) => handleSceneDurationChange(scene.id, e.target.value)}
                className="form-control"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SceneList;""",
        
        "Timeline.jsx": """import React from 'react';

const Timeline = ({ scenes, onSceneUpdate }) => {
  const totalDuration = scenes.reduce((sum, scene) => sum + scene.duration, 0);

  return (
    <div className="timeline">
      <div className="timeline-header">
        <h3>⏱️ Timeline</h3>
        <span>Duração Total: {totalDuration}s</span>
      </div>
      
      <div className="timeline-track">
        {scenes.map((scene, index) => {
          const startTime = scenes.slice(0, index).reduce((sum, s) => sum + s.duration, 0);
          const width = (scene.duration / totalDuration) * 100;
          const left = (startTime / totalDuration) * 100;
          
          return (
            <div
              key={scene.id}
              className="timeline-scene"
              style={{
                position: 'absolute',
                left: `${left}%`,
                width: `${width}%`,
                height: '80%',
                top: '10%',
                backgroundColor: '#2196f3',
                border: '1px solid #1976d2',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '12px',
                cursor: 'pointer'
              }}
            >
              {scene.name}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Timeline;""",
        
        "EditorCanvas.jsx": """import React from 'react';

const EditorCanvas = ({ selectedScene, assets }) => {
  if (!selectedScene) {
    return (
      <div className="canvas-container">
        <div className="canvas-placeholder">
          <h3>Selecione uma cena para editar</h3>
          <p>Use a lista de cenas à esquerda para selecionar uma cena</p>
        </div>
      </div>
    );
  }

  return (
    <div className="canvas-container">
      <div className="canvas-header">
        <h3>Editando: {selectedScene.name}</h3>
        <span>Duração: {selectedScene.duration}s</span>
      </div>
      
      <div className="canvas">
        <div className="canvas-content">
          <div className="scene-preview">
            <h4>Preview da Cena</h4>
            <div className="scene-elements">
              {selectedScene.elements?.map((element, index) => (
                <div key={index} className="scene-element">
                  {element.type}: {element.content}
                </div>
              ))}
            </div>
          </div>
          
          <div className="assets-panel">
            <h4>Assets Disponíveis</h4>
            <div className="assets-grid">
              {assets.map(asset => (
                <div key={asset.id} className="asset-thumbnail">
                  <span>{asset.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditorCanvas;""",
        
        "Toolbar.jsx": """import React from 'react';

const Toolbar = () => {
  const handleSave = () => {
    console.log('Salvando projeto...');
  };

  const handleExport = () => {
    console.log('Exportando vídeo...');
  };

  const handlePreview = () => {
    console.log('Visualizando preview...');
  };

  return (
    <div className="toolbar">
      <div className="toolbar-left">
        <button onClick={handleSave} className="btn">
          💾 Salvar
        </button>
        <button onClick={handlePreview} className="btn btn-secondary">
          👁️ Preview
        </button>
      </div>
      
      <div className="toolbar-right">
        <button onClick={handleExport} className="btn">
          🎬 Exportar Vídeo
        </button>
      </div>
    </div>
  );
};

export default Toolbar;"""
    }
    
    for filename, content in components.items():
        with open(f"src/components/{filename}", "w", encoding="utf-8") as f:
            f.write(content)
    
    print_colored("✅ Componentes criados!", Colors.GREEN)

def test_react_app():
    """Testar se o React App funciona"""
    print_colored("🧪 Testando React App...", Colors.BLUE)
    
    try:
        # Tentar iniciar o servidor de desenvolvimento
        process = subprocess.Popen(
            ["npm", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar um pouco para ver se inicia
        time.sleep(10)
        
        # Verificar se o processo ainda está rodando
        if process.poll() is None:
            print_colored("✅ React App iniciado com sucesso!", Colors.GREEN)
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print_colored(f"❌ Erro ao iniciar React App: {stderr}", Colors.RED)
            return False
    except Exception as e:
        print_colored(f"❌ Erro ao testar React App: {e}", Colors.RED)
        return False

def create_start_scripts():
    """Criar scripts de inicialização"""
    print_colored("📜 Criando scripts de inicialização...", Colors.BLUE)
    
    # Script para iniciar frontend
    start_frontend_js = """#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Iniciando TecnoCursos AI Frontend...');

const frontendProcess = spawn('npm', ['start'], {
  stdio: 'inherit',
  cwd: __dirname
});

frontendProcess.on('close', (code) => {
  console.log(`Frontend finalizado com código ${code}`);
});

process.on('SIGINT', () => {
  console.log('\\n🛑 Finalizando frontend...');
  frontendProcess.kill('SIGINT');
  process.exit(0);
});"""
    
    with open("start_frontend.js", "w", encoding="utf-8") as f:
        f.write(start_frontend_js)
    
    # Script batch para Windows
    start_frontend_bat = """@echo off
echo 🚀 Iniciando TecnoCursos AI Frontend...
npm start
pause"""
    
    with open("start_frontend.bat", "w", encoding="utf-8") as f:
        f.write(start_frontend_bat)
    
    print_colored("✅ Scripts de inicialização criados!", Colors.GREEN)

def main():
    """Função principal"""
    print_header("CORREÇÃO AUTOMÁTICA DO FRONTEND - TECNOCURSOSAI")
    
    print_colored("🎯 Iniciando correção automática do frontend...\n", Colors.BLUE)
    
    # Verificar Node.js e NPM
    if not check_node_installation():
        print_colored("❌ Node.js não encontrado. Instale o Node.js primeiro.", Colors.RED)
        return False
    
    if not check_npm_installation():
        print_colored("❌ NPM não encontrado. Instale o NPM primeiro.", Colors.RED)
        return False
    
    # Limpar node_modules
    force_clean_node_modules()
    
    # Criar estrutura React
    create_react_app_structure()
    create_main_app_component()
    create_css_styles()
    create_index_js()
    create_index_css()
    create_component_files()
    create_start_scripts()
    
    # Instalar dependências
    if not install_dependencies():
        print_colored("❌ Falha na instalação das dependências!", Colors.RED)
        return False
    
    # Testar aplicação
    if test_react_app():
        print_colored("\n🎉 FRONTEND CORRIGIDO COM SUCESSO!", Colors.GREEN)
        print_colored("\n📋 PRÓXIMOS PASSOS:", Colors.CYAN)
        print_colored("1. Execute: npm start", Colors.WHITE)
        print_colored("2. Acesse: http://localhost:3000", Colors.WHITE)
        print_colored("3. O backend deve estar rodando em: http://localhost:8000", Colors.WHITE)
        return True
    else:
        print_colored("\n❌ Falha no teste do frontend!", Colors.RED)
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print_colored("\n✅ Correção do frontend concluída com sucesso!", Colors.GREEN)
        else:
            print_colored("\n❌ Correção do frontend falhou!", Colors.RED)
            sys.exit(1)
    except KeyboardInterrupt:
        print_colored("\n⚠️ Operação interrompida pelo usuário!", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ Erro inesperado: {e}", Colors.RED)
        sys.exit(1) 