import { Navigate, Route, Routes } from 'react-router-dom';
import { withAuth } from '../hooks/useAuth';
import Dashboard from '../pages/Dashboard';
import Editor from '../pages/Editor';
import Login from '../pages/Login';
import ProjectList from '../pages/ProjectList';

const ProtectedDashboard = withAuth(Dashboard);
const ProtectedEditor = withAuth(Editor);
const ProtectedProjectList = withAuth(ProjectList);

const AppRoutes = () => {
  return (
    <Routes>
      <Route path='/login' element={<Login />} />
      <Route path='/dashboard' element={<ProtectedDashboard />} />
      <Route path='/editor' element={<ProtectedEditor />} />
      <Route path='/editor/:projectId' element={<ProtectedEditor />} />
      <Route path='/projects' element={<ProtectedProjectList />} />
      <Route path='/' element={<Navigate to='/dashboard' replace />} />
    </Routes>
  );
};

export default AppRoutes;
