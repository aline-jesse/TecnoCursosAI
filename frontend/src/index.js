import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

// Configuração para desenvolvimento
const rootElement = document.getElementById('root');

if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);

  root.render(
    React.createElement(React.StrictMode, null, React.createElement(App))
  );
} else {
  // console.error('Elemento root não encontrado');
}
