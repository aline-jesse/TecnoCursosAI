// TecnoCursos AI - JavaScript Principal

// Global error handlers to prevent uncaught promise rejections and errors
window.addEventListener('error', (event) => {
    console.log('Global error caught:', event.error?.message || event.message);
    // Prevent default browser error handling for some extension-related errors
    if (event.error?.message?.includes('message channel')) {
        event.preventDefault();
    }
});

window.addEventListener('unhandledrejection', (event) => {
    console.log('Unhandled promise rejection:', event.reason?.message || event.reason);
    // Prevent default handling for extension-related rejections
    if (event.reason?.message?.includes('message channel')) {
        event.preventDefault();
    }
});

class TecnoCursosAPI {
    constructor(baseURL = null) {
        // Força sempre usar a porta 8000 para a API, independente da página atual
        if (!baseURL) {
            const {protocol} = window.location;
            const {hostname} = window.location;
            this.baseURL = `${protocol}//${hostname}:8000/api`;
        } else {
            this.baseURL = baseURL;
        }
        this.token = localStorage.getItem('token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        this.ws = null;
    }

    // Configuração de Headers
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    // Método genérico para requests - with improved error handling
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await Promise.race([
                fetch(url, config),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Request timeout')), 30000)
                )
            ]);
            
            if (response.status === 401 && this.refreshToken) {
                try {
                    await this.refreshAccessToken();
                    config.headers['Authorization'] = `Bearer ${this.token}`;
                    return await fetch(url, config);
                } catch (refreshError) {
                    console.log('Token refresh failed:', refreshError.message);
                    this.logout();
                    throw new Error('Sessão expirada. Faça login novamente.');
                }
            }

            if (!response.ok) {
                let errorMessage = 'Erro na requisição';
                try {
                    const error = await response.json();
                    errorMessage = error.detail || error.message || errorMessage;
                } catch (parseError) {
                    console.log('Error parsing response:', parseError.message);
                }
                throw new Error(errorMessage);
            }

            return await response.json();
        } catch (error) {
            console.log('Request error:', error.message);
            
            // Handle specific connection errors
            if (error.message.includes('ERR_CONNECTION_REFUSED')) {
                throw new Error('⚠️ Backend não está rodando! Execute: python RESOLVER_CONEXAO_AGORA.py');
            }
            
            if (error.message.includes('Failed to fetch')) {
                throw new Error('🔌 Erro de conexão. Verifique se o servidor está rodando na porta 8000');
            }
            
            // Handle network errors gracefully
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Erro de conexão. Verifique sua internet.');
            }
            
            throw error;
        }
    }

    // Autenticação
    async login(email, password) {
        try {
            const response = await this.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });

            this.token = response.access_token;
            this.refreshToken = response.refresh_token;
            this.user = response.user;

            localStorage.setItem('token', this.token);
            localStorage.setItem('refresh_token', this.refreshToken);
            localStorage.setItem('user', JSON.stringify(this.user));

            return response;
        } catch (error) {
            throw error;
        }
    }

    async register(userData) {
        return await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async refreshAccessToken() {
        if (!this.refreshToken) {
            this.logout();
            return;
        }

        try {
            const response = await this.request('/auth/refresh', {
                method: 'POST',
                body: JSON.stringify({ refresh_token: this.refreshToken })
            });

            this.token = response.access_token;
            localStorage.setItem('token', this.token);
        } catch (error) {
            this.logout();
            throw error;
        }
    }

    logout() {
        this.token = null;
        this.refreshToken = null;
        this.user = null;
        localStorage.clear();
        if (this.ws) {
            this.ws.close();
        }
        window.location.href = '/login.html';
    }

    // Projetos
    async getProjects() {
        return await this.request('/projects/');
    }

    async createProject(projectData) {
        return await this.request('/projects/', {
            method: 'POST',
            body: JSON.stringify(projectData)
        });
    }

    async updateProject(projectId, projectData) {
        return await this.request(`/projects/${projectId}`, {
            method: 'PUT',
            body: JSON.stringify(projectData)
        });
    }

    async deleteProject(projectId) {
        return await this.request(`/projects/${projectId}`, {
            method: 'DELETE'
        });
    }

    // Upload de arquivos
    async uploadFile(file, projectId = null, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        if (projectId) {
            formData.append('project_id', projectId);
        }
        
        // Adicionar opções extras
        if (options.autoCreateProject !== undefined) {
            formData.append('auto_create_project', options.autoCreateProject);
        }
        
        if (options.description) {
            formData.append('description', options.description);
        }

        const response = await fetch(`${this.baseURL}/files/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro no upload');
        }

        return await response.json();
    }

    async getFiles(projectId) {
        return await this.request(`/files/?project_id=${projectId}`);
    }

    async deleteFile(fileId) {
        return await this.request(`/files/${fileId}`, {
            method: 'DELETE'
        });
    }

    // Criar projeto rapidamente
    async createQuickProject(name = null, description = null) {
        const body = {};
        if (name) body.name = name;
        if (description) body.description = description;
        
        const response = await fetch(`${this.baseURL}/projects/quick-create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar projeto');
        }

        return await response.json();
    }

    // Verificar projetos do usuário 
    async checkProjects() {
        const response = await fetch(`${this.baseURL}/files/check-projects`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao verificar projetos');
        }

        return await response.json();
    }

    // Verificar status de upload
    async checkUploadStatus(uploadId) {
        try {
            const response = await fetch(`${this.baseURL}/files/upload-status/${uploadId}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao verificar status');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            return null;
        }
    }

    // Obter uploads recentes
    async getRecentUploads(limit = 10) {
        try {
            const response = await fetch(`${this.baseURL}/files/recent-uploads?limit=${limit}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao buscar uploads recentes');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar uploads recentes:', error);
            return { uploads: [], total: 0 };
        }
    }

    // Monitorar progresso de upload
    async monitorUploadProgress(uploadId, callback) {
        const maxAttempts = 30; // 5 minutos máximo
        let attempts = 0;

        const checkStatus = async () => {
            attempts++;
            const status = await this.checkUploadStatus(uploadId);
            
            if (status) {
                callback(status);
                
                if (status.status === 'completed' || status.status === 'failed' || attempts >= maxAttempts) {
                    return; // Para o monitoramento
                }
            }

            // Continuar verificando a cada 10 segundos
            setTimeout(checkStatus, 10000);
        };

        // Iniciar monitoramento
        checkStatus();
    }

    // Atualizar interface com uploads recentes
    async updateRecentUploadsUI() {
        const recentData = await this.getRecentUploads(5);
        const container = document.querySelector('.recent-uploads-container');
        
        if (container && recentData.uploads.length > 0) {
            container.innerHTML = `
                <h6>📄 Uploads Recentes</h6>
                <div class="list-group list-group-flush">
                    ${recentData.uploads.map(upload => `
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <small class="fw-bold">${upload.filename}</small>
                                <br>
                                <small class="text-muted">${upload.project_name}</small>
                            </div>
                            <span class="badge ${upload.status === 'completed' ? 'bg-success' : 'bg-warning'} rounded-pill">
                                ${upload.status === 'completed' ? '✅' : '⏳'}
                            </span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    // WebSocket para atualizações em tempo real
    connectWebSocket() {
        if (!this.token) return;

        const wsURL = `ws://localhost:8000/ws?token=${this.token}`;
        this.ws = new WebSocket(wsURL);

        this.ws.onopen = () => {
            console.log('WebSocket conectado');
            showNotification('Conectado ao servidor', 'success');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket desconectado');
            setTimeout(() => this.connectWebSocket(), 5000);
        };

        this.ws.onerror = (error) => {
            console.error('Erro WebSocket:', error);
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'file_uploaded':
                showNotification(`Arquivo ${data.filename} enviado com sucesso!`, 'success');
                if (window.loadFiles) window.loadFiles();
                break;
            case 'file_processed':
                showNotification(`Arquivo ${data.filename} processado!`, 'info');
                if (window.loadFiles) window.loadFiles();
                break;
            case 'project_updated':
                showNotification('Projeto atualizado', 'info');
                if (window.loadProjects) window.loadProjects();
                break;
        }
    }

    // Estatísticas
    async getStats() {
        return await this.request('/stats/dashboard');
    }
}

// Instância global da API
const api = new TecnoCursosAPI();

// Utilitários de UI
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} slide-up`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <strong>${type === 'success' ? '✓' : type === 'danger' ? '✗' : 'ℹ'}</strong>
        ${message}
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, duration);
}

function showModal(title, content, actions = []) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content bounce-in">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="close" onclick="closeModal(this)">&times;</button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            <div class="modal-footer">
                ${actions.map(action => `
                    <button class="btn btn-${action.type || 'primary'}" 
                            onclick="${action.onclick}">${action.text}</button>
                `).join('')}
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    return modal;
}

function closeModal(element) {
    const modal = element.closest('.modal');
    if (modal) {
        modal.remove();
    }
}

function showSpinner(element) {
    element.innerHTML = '<div class="spinner"></div>';
}

function hideSpinner(element, originalContent) {
    element.innerHTML = originalContent;
}

// Formatação de dados
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))  } ${  sizes[i]}`;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('pt-BR');
}

function getFileIcon(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    switch (extension) {
        case 'pdf':
            return '📄';
        case 'pptx':
        case 'ppt':
            return '📊';
        case 'mp4':
        case 'avi':
        case 'mov':
            return '🎥';
        default:
            return '📁';
    }
}

// Validação de formulários
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
    });

    return isValid;
}

// Upload de arquivos com drag & drop
function initFileUpload(element, onFileSelect) {
    const fileInput = element.querySelector('input[type="file"]');
    
    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        element.classList.add('dragover');
    });

    element.addEventListener('dragleave', () => {
        element.classList.remove('dragover');
    });

    element.addEventListener('drop', (e) => {
        e.preventDefault();
        element.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        onFileSelect(files);
    });

    element.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        onFileSelect(files);
    });
}

// Progress bar
function updateProgress(element, percentage) {
    const progressBar = element.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = `${Math.round(percentage)}%`;
    }
}

// Autenticação e navegação
function requireAuth() {
    if (!api.token || !api.user) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

function updateUserInfo() {
    if (api.user) {
        const userElements = document.querySelectorAll('[data-user-name]');
        userElements.forEach(el => {
            el.textContent = api.user.full_name || api.user.email;
        });

        const avatarElements = document.querySelectorAll('[data-user-avatar]');
        avatarElements.forEach(el => {
            el.textContent = (api.user.full_name || api.user.email).charAt(0).toUpperCase();
        });
    }
}

// Pesquisa e filtros
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function filterTable(tableSelector, searchInput) {
    const table = document.querySelector(tableSelector);
    const rows = table.querySelectorAll('tbody tr');
    const searchTerm = searchInput.value.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// Eventos globais
document.addEventListener('DOMContentLoaded', () => {
    // Conectar WebSocket se autenticado
    if (api.token) {
        api.connectWebSocket();
        updateUserInfo();
    }

    // Setup de logout
    const logoutButtons = document.querySelectorAll('[data-logout]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Tem certeza que deseja sair?')) {
                api.logout();
            }
        });
    });

    // Setup de pesquisa com debounce
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        const target = input.getAttribute('data-search');
        const debouncedFilter = debounce(() => filterTable(target, input), 300);
        input.addEventListener('input', debouncedFilter);
    });

    // Auto-refresh para páginas com dados dinâmicos
    if (document.querySelector('[data-auto-refresh]')) {
        setInterval(() => {
            if (document.visibilityState === 'visible') {
                const refreshElements = document.querySelectorAll('[data-auto-refresh]');
                refreshElements.forEach(el => {
                    const functionName = el.getAttribute('data-auto-refresh');
                    if (window[functionName]) {
                        window[functionName]();
                    }
                });
            }
        }, 30000); // Refresh a cada 30 segundos
    }
});

// Funções auxiliares para páginas específicas
window.showNotification = showNotification;
window.showModal = showModal;
window.closeModal = closeModal;
window.formatFileSize = formatFileSize;
window.formatDate = formatDate;
window.getFileIcon = getFileIcon;
window.validateForm = validateForm;
window.initFileUpload = initFileUpload;
window.updateProgress = updateProgress;
window.requireAuth = requireAuth;
window.updateUserInfo = updateUserInfo;
window.api = api; 