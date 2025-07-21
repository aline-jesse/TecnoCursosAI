/**
 * Hook de Autenticação com Context API
 *
 * Fornece estado global de autenticação e funções auxiliares
 */

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from 'react';
import authService from '../services/authService';
import { useNotification } from './useNotification';

// Criar contexto
const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  updateProfile: async () => {},
  refreshUser: async () => {},
});

/**
 * Provider de Autenticação
 * Envolve toda a aplicação para fornecer contexto de auth
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const { showSuccess, showError, showInfo } = useNotification();

  // Verificar autenticação ao montar
  useEffect(() => {
    checkAuth();
  }, []);

  /**
   * Verificar se usuário está autenticado
   */
  const checkAuth = async () => {
    try {
      setIsLoading(true);

      if (authService.isAuthenticated()) {
        // Se tem token válido, buscar dados do usuário
        const currentUser = authService.getCurrentUser();

        if (currentUser) {
          setUser(currentUser);
        } else {
          // Buscar dados do servidor
          const userData = await authService.fetchCurrentUser();
          setUser(userData);
        }
      } else {
        // Limpar dados se não está autenticado
        setUser(null);
      }
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Login do usuário
   */
  const login = useCallback(
    async (email, password) => {
      try {
        setIsLoading(true);
        const userData = await authService.login(email, password);
        setUser(userData);
        showSuccess('Login realizado com sucesso!');
        return userData;
      } catch (error) {
        const message = error.response?.data?.detail || 'Erro ao fazer login';
        showError(message);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [showSuccess, showError]
  );

  /**
   * Registro de novo usuário
   */
  const register = useCallback(
    async userData => {
      try {
        setIsLoading(true);
        const newUser = await authService.register(userData);
        setUser(newUser);
        showSuccess('Cadastro realizado com sucesso!');
        return newUser;
      } catch (error) {
        const message = error.response?.data?.detail || 'Erro ao criar conta';
        showError(message);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [showSuccess, showError]
  );

  /**
   * Logout do usuário
   */
  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      await authService.logout();
      setUser(null);
      showInfo('Logout realizado com sucesso!');
    } catch (error) {
      showError('Erro ao fazer logout');
    } finally {
      setIsLoading(false);
    }
  }, [showInfo, showError]);

  /**
   * Atualizar perfil do usuário
   */
  const updateProfile = useCallback(
    async updates => {
      try {
        const updatedUser = await authService.updateProfile(updates);
        setUser(updatedUser);
        showSuccess('Perfil atualizado com sucesso!');
        return updatedUser;
      } catch (error) {
        const message =
          error.response?.data?.detail || 'Erro ao atualizar perfil';
        showError(message);
        throw error;
      }
    },
    [showSuccess, showError]
  );

  /**
   * Recarregar dados do usuário
   */
  const refreshUser = useCallback(async () => {
    try {
      const userData = await authService.fetchCurrentUser();
      setUser(userData);
      return userData;
    } catch (error) {
      console.error('Erro ao atualizar dados do usuário:', error);
      throw error;
    }
  }, []);

  // Valor do contexto
  const contextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

/**
 * Hook para usar o contexto de autenticação
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }

  return context;
};

/**
 * HOC para proteger rotas que requerem autenticação
 */
export const withAuth = Component => {
  return props => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
      return (
        <div className='flex items-center justify-center min-h-screen'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600'></div>
        </div>
      );
    }

    if (!isAuthenticated) {
      window.location.href = '/login';
      return null;
    }

    return <Component {...props} />;
  };
};

/**
 * Hook para verificar permissões
 */
export const usePermissions = () => {
  const { user } = useAuth();

  const hasPermission = useCallback(
    permission => {
      if (!user) return false;

      // Implementar lógica de permissões conforme necessário
      if (user.is_admin) return true;

      return user.permissions?.includes(permission) || false;
    },
    [user]
  );

  const hasRole = useCallback(
    role => {
      if (!user) return false;

      return user.roles?.includes(role) || false;
    },
    [user]
  );

  return {
    hasPermission,
    hasRole,
  };
};
