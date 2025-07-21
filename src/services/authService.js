/**
 * Serviço de Autenticação - TecnoCursos AI
 *
 * Gerencia autenticação com JWT:
 * - Login e registro de usuários
 * - Armazenamento seguro de tokens
 * - Refresh automático de tokens
 * - Logout e limpeza de sessão
 */

import api from './api';
import { API_ENDPOINTS } from '../config/api.config';
import { jwtDecode } from 'jwt-decode';
import moment from 'moment';

class AuthService {
  constructor() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    this.loadFromStorage();
  }

  /**
   * Carregar dados do localStorage
   */
  loadFromStorage() {
    try {
      const tokenData = localStorage.getItem('token');
      const userData = localStorage.getItem('user');

      if (tokenData) {
        const token = JSON.parse(tokenData);
        this.token = token.access_token;
        this.refreshToken = token.refresh_token;
      }

      if (userData) {
        this.user = JSON.parse(userData);
      }
    } catch (error) {
      console.error('Erro ao carregar dados de autenticação:', error);
      this.clearAuth();
    }
  }

  /**
   * Login do usuário
   *
   * @param {string} email - Email do usuário
   * @param {string} password - Senha do usuário
   * @returns {Promise<Object>} Dados do usuário logado
   */
  async login(email, password) {
    try {
      // Limpar auth header antes do login
      delete api.defaults.headers.common['Authorization'];

      // Fazer login
      const response = await api.post(API_ENDPOINTS.auth.login, {
        username: email, // FastAPI espera username, não email
        password,
      });

      // Salvar tokens
      const tokenData = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type || 'bearer',
      };

      this.setAuthData(tokenData);

      // Buscar dados do usuário
      const user = await this.fetchCurrentUser();

      return user;
    } catch (error) {
      console.error('Erro no login:', error);
      throw error;
    }
  }

  /**
   * Registro de novo usuário
   *
   * @param {Object} userData - Dados do usuário
   * @returns {Promise<Object>} Usuário criado
   */
  async register(userData) {
    try {
      const response = await api.post(API_ENDPOINTS.auth.register, {
        email: userData.email,
        password: userData.password,
        username: userData.username || userData.email.split('@')[0],
        full_name: userData.fullName,
        phone: userData.phone,
        company: userData.company,
      });

      // Após registro bem-sucedido, fazer login automático
      if (response.data && userData.email && userData.password) {
        await this.login(userData.email, userData.password);
      }

      return response.data;
    } catch (error) {
      console.error('Erro no registro:', error);
      throw error;
    }
  }

  /**
   * Buscar dados do usuário atual
   *
   * @returns {Promise<Object>} Dados do usuário
   */
  async fetchCurrentUser() {
    try {
      const response = await api.get(API_ENDPOINTS.auth.me);
      this.user = response.data;
      localStorage.setItem('user', JSON.stringify(this.user));
      return this.user;
    } catch (error) {
      console.error('Erro ao buscar usuário:', error);
      throw error;
    }
  }

  /**
   * Renovar token de acesso
   *
   * @returns {Promise<string>} Novo token de acesso
   */
  async refreshAccessToken() {
    try {
      if (!this.refreshToken) {
        throw new Error('Refresh token não disponível');
      }

      const response = await api.post(API_ENDPOINTS.auth.refresh, {
        refresh_token: this.refreshToken,
      });

      const tokenData = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token || this.refreshToken,
        token_type: response.data.token_type || 'bearer',
      };

      this.setAuthData(tokenData);

      return tokenData.access_token;
    } catch (error) {
      console.error('Erro ao renovar token:', error);
      this.logout();
      throw error;
    }
  }

  /**
   * Logout do usuário
   */
  async logout() {
    try {
      // Tentar fazer logout no backend
      await api.post(API_ENDPOINTS.auth.logout);
    } catch (error) {
      // Continuar com logout local mesmo se falhar no backend
      console.error('Erro ao fazer logout no servidor:', error);
    } finally {
      this.clearAuth();
      window.location.href = '/login';
    }
  }

  /**
   * Limpar dados de autenticação
   */
  clearAuth() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
  }

  /**
   * Salvar dados de autenticação
   *
   * @param {Object} tokenData - Dados do token
   */
  setAuthData(tokenData) {
    this.token = tokenData.access_token;
    this.refreshToken = tokenData.refresh_token;

    localStorage.setItem('token', JSON.stringify(tokenData));

    // Configurar header padrão
    api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
  }

  /**
   * Verificar se o usuário está autenticado
   *
   * @returns {boolean} True se autenticado
   */
  isAuthenticated() {
    if (!this.token) return false;

    try {
      const decoded = jwtDecode(this.token);
      const isValid = moment.unix(decoded.exp).toDate() > new Date();
      return isValid;
    } catch (error) {
      return false;
    }
  }

  /**
   * Verificar se o token precisa ser renovado
   *
   * @returns {boolean} True se precisa renovar
   */
  shouldRefreshToken() {
    if (!this.token) return false;

    try {
      const decoded = jwtDecode(this.token);
      const expirationTime = moment.unix(decoded.exp);
      const now = moment();
      const minutesUntilExpiry = expirationTime.diff(now, 'minutes');

      // Renovar se faltar menos de 5 minutos para expirar
      return minutesUntilExpiry < 5;
    } catch (error) {
      return false;
    }
  }

  /**
   * Obter dados do usuário atual
   *
   * @returns {Object|null} Dados do usuário ou null
   */
  getCurrentUser() {
    return this.user;
  }

  /**
   * Obter token de acesso atual
   *
   * @returns {string|null} Token ou null
   */
  getAccessToken() {
    return this.token;
  }

  /**
   * Atualizar perfil do usuário
   *
   * @param {Object} updates - Dados a atualizar
   * @returns {Promise<Object>} Usuário atualizado
   */
  async updateProfile(updates) {
    try {
      const response = await api.put(API_ENDPOINTS.users.update, updates);
      this.user = response.data;
      localStorage.setItem('user', JSON.stringify(this.user));
      return this.user;
    } catch (error) {
      console.error('Erro ao atualizar perfil:', error);
      throw error;
    }
  }

  /**
   * Alterar senha do usuário
   *
   * @param {string} currentPassword - Senha atual
   * @param {string} newPassword - Nova senha
   * @returns {Promise<void>}
   */
  async changePassword(currentPassword, newPassword) {
    try {
      await api.post('/api/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
    } catch (error) {
      console.error('Erro ao alterar senha:', error);
      throw error;
    }
  }
}

// Exportar instância única (singleton)
export default new AuthService();
