import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App_importmap.jsx';
import './index.css';

// Configuração para desenvolvimento
const rootElement = document.getElementById('root');

if (rootElement) {
  const root = createRoot(rootElement);
  
  root.render(
    React.createElement(React.StrictMode, null,
      React.createElement(App)
    )
  );
} else {
  console.error('Elemento root não encontrado');
} 