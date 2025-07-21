/**
 * Dashboard JavaScript - TecnoCursosAI
 * Funcionalidades interativas para o dashboard
 * 
 * Inclui:
 * - Auto-refresh configurável
 * - Animações dinâmicas
 * - Interações do usuário
 * - Formatação de dados
 */

class Dashboard {
    constructor() {
        this.autoRefreshInterval = null;
        this.refreshRate = 30000; // 30 segundos
        this.isAutoRefreshEnabled = false;
        
        this.init();
    }
    
    init() {
        console.log('🎬 TecnoCursosAI Dashboard initialized');
        
        this.setupEventListeners();
        this.formatTimestamps();
        this.setupMetricAnimations();
        this.setupAutoRefresh();
        this.setupKeyboardShortcuts();
    }
    
    /**
     * Configura event listeners para interações
     */
    setupEventListeners() {
        // Toggle de auto-refresh (se houver botão)
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.toggleAutoRefresh(e.target.checked);
            });
        }
        
        // Refresh manual
        const refreshButton = document.getElementById('refresh-button');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.manualRefresh();
            });
        }
        
        // Cards clicáveis para componentes
        document.querySelectorAll('.component-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('a')) {
                    this.showComponentDetails(card);
                }
            });
        });
        
        // Hover effects para métricas
        document.querySelectorAll('.metric-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.animateMetricBar(card);
            });
        });
    }
    
    /**
     * Formata timestamps para formato brasileiro
     */
    formatTimestamps() {
        document.querySelectorAll('[data-timestamp]').forEach(element => {
            const timestamp = element.getAttribute('data-timestamp');
            const date = new Date(timestamp);
            element.textContent = date.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        });
        
        // Formatar timestamp principal
        const lastUpdated = document.getElementById('last-updated');
        if (lastUpdated && lastUpdated.textContent) {
            try {
                const date = new Date(lastUpdated.textContent);
                lastUpdated.textContent = date.toLocaleString('pt-BR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (e) {
                console.warn('Erro ao formatar timestamp:', e);
            }
        }
    }
    
    /**
     * Configura animações para barras de métricas
     */
    setupMetricAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateMetricBar(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        document.querySelectorAll('.metric-card').forEach(card => {
            observer.observe(card);
        });
    }
    
    /**
     * Anima barra de progresso de uma métrica
     */
    animateMetricBar(card) {
        const bar = card.querySelector('.metric-fill');
        if (bar) {
            const originalWidth = bar.style.width;
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.width = originalWidth;
            }, 100);
        }
    }
    
    /**
     * Configura sistema de auto-refresh
     */
    setupAutoRefresh() {
        // Verifica se deve ativar auto-refresh baseado em localStorage
        const autoRefreshEnabled = localStorage.getItem('dashboard-auto-refresh') === 'true';
        if (autoRefreshEnabled) {
            this.enableAutoRefresh();
        }
        
        // Adiciona indicador visual de próximo refresh
        this.updateRefreshIndicator();
    }
    
    /**
     * Ativa/desativa auto-refresh
     */
    toggleAutoRefresh(enabled) {
        if (enabled) {
            this.enableAutoRefresh();
        } else {
            this.disableAutoRefresh();
        }
        
        localStorage.setItem('dashboard-auto-refresh', enabled.toString());
    }
    
    /**
     * Ativa auto-refresh
     */
    enableAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        this.isAutoRefreshEnabled = true;
        this.autoRefreshInterval = setInterval(() => {
            this.refresh();
        }, this.refreshRate);
        
        console.log(`🔄 Auto-refresh ativado (${this.refreshRate / 1000}s)`);
        this.showNotification('Auto-refresh ativado', 'success');
    }
    
    /**
     * Desativa auto-refresh
     */
    disableAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
        
        this.isAutoRefreshEnabled = false;
        console.log('⏸️ Auto-refresh desativado');
        this.showNotification('Auto-refresh desativado', 'info');
    }
    
    /**
     * Refresh manual da página
     */
    manualRefresh() {
        this.showNotification('Atualizando dashboard...', 'info');
        this.refresh();
    }
    
    /**
     * Executa refresh da página
     */
    refresh() {
        // Adiciona parâmetro para evitar cache
        const url = new URL(window.location);
        url.searchParams.set('_refresh', Date.now().toString());
        window.location.href = url.toString();
    }
    
    /**
     * Atualiza indicador de próximo refresh
     */
    updateRefreshIndicator() {
        const indicator = document.getElementById('refresh-indicator');
        if (!indicator || !this.isAutoRefreshEnabled) return;
        
        let timeLeft = this.refreshRate / 1000;
        
        const updateTimer = () => {
            if (timeLeft <= 0 || !this.isAutoRefreshEnabled) {
                return;
            }
            
            indicator.textContent = `Próximo refresh em ${timeLeft}s`;
            timeLeft--;
            
            setTimeout(updateTimer, 1000);
        };
        
        updateTimer();
    }
    
    /**
     * Configura atalhos de teclado
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + R = Refresh manual
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                this.manualRefresh();
            }
            
            // F5 = Refresh manual
            if (e.key === 'F5') {
                e.preventDefault();
                this.manualRefresh();
            }
            
            // Ctrl/Cmd + Shift + A = Toggle auto-refresh
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'A') {
                e.preventDefault();
                this.toggleAutoRefresh(!this.isAutoRefreshEnabled);
            }
        });
    }
    
    /**
     * Mostra detalhes de um componente
     */
    showComponentDetails(card) {
        const componentName = card.querySelector('h4').textContent;
        const status = card.querySelector('.component-status-badge').textContent;
        const description = card.querySelector('.component-description').textContent;
        const details = card.querySelector('.component-details small').textContent;
        
        // Cria modal simples ou alerta
        const message = `
Componente: ${componentName}
Status: ${status}
Descrição: ${description}
Detalhes: ${details}
        `.trim();
        
        alert(message); // Em produção, usar modal mais elegante
    }
    
    /**
     * Mostra notificação toast simples
     */
    showNotification(message, type = 'info') {
        // Verifica se existe sistema de toast implementado
        if (window.toast && typeof window.toast.show === 'function') {
            window.toast.show(message, type);
            return;
        }
        
        // Fallback: criar notificação simples
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remover após 3 segundos
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    /**
     * Utilitários para desenvolvedores
     */
    static utils = {
        /**
         * Força refresh do dashboard
         */
        forceRefresh() {
            window.location.reload(true);
        },
        
        /**
         * Exporta dados do dashboard como JSON
         */
        exportData() {
            const data = {
                timestamp: new Date().toISOString(),
                components: Array.from(document.querySelectorAll('.component-card')).map(card => ({
                    name: card.querySelector('h4').textContent,
                    status: card.querySelector('.component-status-badge').textContent.trim(),
                    description: card.querySelector('.component-description').textContent
                })),
                metrics: Array.from(document.querySelectorAll('.metric-card')).map(card => ({
                    label: card.querySelector('.metric-label').textContent,
                    value: card.querySelector('.metric-value').textContent
                }))
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dashboard-data-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        },
        
        /**
         * Toggle modo debug
         */
        toggleDebug() {
            document.body.classList.toggle('debug-mode');
            console.log('Debug mode:', document.body.classList.contains('debug-mode') ? 'ON' : 'OFF');
        }
    };
}

// Inicializar dashboard quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Expor utilitários globalmente para debug
window.dashboardUtils = Dashboard.utils;

// Console helper
console.log('🎬 TecnoCursosAI Dashboard JS loaded');
console.log('💡 Comandos disponíveis:');
console.log('   - dashboard.toggleAutoRefresh(true/false)');
console.log('   - dashboard.manualRefresh()');
console.log('   - dashboardUtils.exportData()');
console.log('   - dashboardUtils.toggleDebug()');
console.log('');
console.log('⌨️  Atalhos de teclado:');
console.log('   - Ctrl+R / F5: Refresh manual');
console.log('   - Ctrl+Shift+A: Toggle auto-refresh'); 