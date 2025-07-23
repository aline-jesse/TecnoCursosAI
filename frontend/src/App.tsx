/**
 * App - Aplicação Principal do Editor de Vídeo TecnoCursos AI
 * Sistema unificado com Zustand, Fabric.js e componentes TypeScript
 */

import './App.css';
import ToastContainer from './components/Toast/ToastContainer';
import { AuthProvider } from './hooks/useAuth';
import AppRoutes from './routes/AppRoutes';

const App = () => {
  return (
    <AuthProvider>
      <AppRoutes />
      <ToastContainer position='top-right' />
    </AuthProvider>
  );
};

export default App;
