# 🎬 Dashboard TecnoCursos AI - Guia de Customização

**Status: ✅ 100% Implementado e Funcional**

## 📋 Visão Geral

O TecnoCursos AI agora possui um dashboard moderno e responsivo na rota principal `/`, inspirado nas melhores práticas dos projetos [FastAPI Dashboard](https://github.com/konekoya/fastapi-dashboard) e [FastAPI Soft UI Dashboard](https://github.com/app-generator/fastapi-soft-ui-dashboard).

### ✨ Funcionalidades Principais

- 🎨 **Design Moderno**: Interface com gradientes, cards e animações suaves
- 📊 **Status em Tempo Real**: Monitoramento de componentes e métricas do sistema
- 🔔 **Integração com Notificações**: Sistema de toast e WebSocket integrado
- 📱 **Responsivo**: Otimizado para desktop, tablet e mobile
- ⚡ **Performance**: Carregamento rápido com lazy loading e otimizações
- 🛠️ **Personalizável**: Fácil customização de cores, textos e componentes

## 🏗️ Arquitetura

### Estrutura de Arquivos
```
TecnoCursosAI/
├── main.py                          # FastAPI principal com dashboard
├── app/
│   ├── routers/
│   │   ├── dashboard.py              # Router do dashboard
│   │   └── notifications.py          # API de notificações
│   └── services/
│       ├── logging_service.py        # Sistema de logs
│       └── notification_service.py   # Notificações em tempo real
├── templates/
│   ├── dashboard.html                # Template principal
│   ├── 404.html                      # Página de erro 404
│   └── 500.html                      # Página de erro 500
├── static/
│   ├── css/
│   │   └── dashboard.css             # Estilos principais
│   ├── js/
│   │   └── dashboard.js              # Funcionalidades interativas
│   └── favicon.ico                   # Ícone do site
└── logs/                             # Logs da aplicação (auto-criado)
```

### Tecnologias Utilizadas

- **Backend**: FastAPI, Jinja2Templates, Pydantic, WebSocket
- **Frontend**: HTML5, CSS3 (Custom), JavaScript (Vanilla)
- **Monitoramento**: psutil, logging estruturado
- **Design System**: Variáveis CSS, gradientes, animações

## 🚀 Como Executar

### 1. Instalação de Dependências

```bash
# Instalar dependências Python
pip install fastapi uvicorn jinja2 python-multipart psutil

# Para desenvolvimento com auto-reload
pip install python-dotenv
```

### 2. Configuração do Ambiente

Crie um arquivo `.env` (opcional):

```bash
# Configurações do sistema
SYSTEM_NAME=TecnoCursosAI
SYSTEM_VERSION=2.0.0
ENVIRONMENT=development

# Configurações de logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/application.log

# Configurações de notificações
NOTIFICATION_CLEANUP_INTERVAL=3600
WEBSOCKET_HEARTBEAT_INTERVAL=30
```

### 3. Executar a Aplicação

```bash
# Desenvolvimento (com auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Produção (com múltiplos workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Acessar o Dashboard

- **Dashboard Principal**: http://localhost:8000/
- **Documentação API**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🎨 Customização

### 1. Personalizar Informações do Sistema

Edite o arquivo `app/routers/dashboard.py`:

```python
class DashboardService:
    def __init__(self):
        # Altere estas configurações
        self.system_name = "Seu Sistema"
        self.system_version = "1.0.0"
        self.environment = "production"
    
    async def get_system_info(self):
        return {
            "name": self.system_name,
            "subtitle": "Sua descrição personalizada",
            "version": self.system_version,
            # ... resto das configurações
        }
```

**Ou use variáveis de ambiente** (recomendado):

```python
self.system_name = os.getenv("SYSTEM_NAME", "Seu Sistema Padrão")
```

### 2. Adicionar Novos Componentes

Para adicionar um novo componente ao monitoramento:

```python
async def get_component_status(self):
    components = []
    
    # Adicione seu novo componente aqui
    try:
        # Sua lógica de verificação
        api_status = await check_external_api()
        
        components.append({
            "name": "API Externa",
            "status": "online" if api_status else "error",
            "description": "Integração com serviço externo",
            "icon": "🌐",
            "details": f"Última resposta: {api_status.response_time}ms"
        })
    except Exception as e:
        components.append({
            "name": "API Externa",
            "status": "error",
            "description": f"Erro na integração: {str(e)}",
            "icon": "🌐",
            "details": "Verificar configuração"
        })
    
    return components
```

### 3. Personalizar Cores e Visual

Edite o arquivo `static/css/dashboard.css`:

```css
:root {
  /* Suas cores personalizadas */
  --primary-color: #your-color;
  --secondary-color: #your-secondary;
  
  /* Seu gradiente personalizado */
  --gradient-bg: linear-gradient(135deg, #your-color1 0%, #your-color2 100%);
  
  /* Sua fonte personalizada */
  --font-family: 'SuaFonte', sans-serif;
}
```

### 4. Adicionar Novas Ações Rápidas

```python
async def get_quick_actions(self):
    return [
        # Suas ações personalizadas
        {
            "title": "Sua Nova Ação",
            "description": "Descrição da ação",
            "url": "/sua-rota",
            "icon": "🚀",
            "color": "purple"
        },
        # ... outras ações
    ]
```

### 5. Customizar Métricas

```python
async def get_system_metrics(self):
    return {
        # Suas métricas personalizadas
        "custom_metric": your_calculation(),
        "business_kpi": await get_business_metric(),
        # ... métricas padrão
    }
```

### 6. Modificar o Template HTML

Edite `templates/dashboard.html` para:

- Alterar a estrutura do layout
- Adicionar novos componentes visuais
- Modificar a organização das seções
- Adicionar metadados específicos

```html
<!-- Adicione suas seções personalizadas -->
<section class="custom-section">
    <div class="section-header">
        <h3>🎯 Sua Seção Personalizada</h3>
        <p>Descrição da seção</p>
    </div>
    
    <div class="custom-grid">
        <!-- Seu conteúdo aqui -->
    </div>
</section>
```

## 📊 Monitoramento e Métricas

### Sistema de Logging

O dashboard integra com o sistema de logging estruturado:

```python
from app.services.logging_service import logging_service, LogLevel, LogCategory

# Log básico
await logging_service.log(
    LogLevel.INFO,
    LogCategory.USER_ACTION,
    "Ação executada",
    user_id="user123",
    metadata={"dados": "extras"}
)

# Context manager para operações
async with logging_service.operation_context("operacao_nome", user_id) as op_id:
    # Sua operação - log automático de sucesso/erro
    await sua_operacao()
```

### Notificações em Tempo Real

Integração com sistema de notificações:

```python
from app.services.notification_service import notification_service

# Notificação simples
await notification_service.notify_success(
    title="Operação Concluída!",
    message="Sua operação foi executada com sucesso",
    user_id="user123"
)

# WebSocket para tempo real
# Conecte em: ws://localhost:8000/notifications/ws/{user_id}
```

### Health Check Personalizado

```python
@router.get("/health")
async def health_check():
    # Adicione suas verificações
    custom_checks = await your_health_checks()
    
    return {
        "status": "healthy",
        "custom_data": custom_checks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

## 🔧 Configurações Avançadas

### 1. Auto-Refresh do Dashboard

JavaScript automático (desabilitado por padrão):

```javascript
// Em static/js/dashboard.js, descomente:
setInterval(() => {
    window.location.reload();
}, 30000); // 30 segundos
```

### 2. Middleware Personalizado

```python
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # Sua lógica personalizada
    start_time = time.time()
    
    response = await call_next(request)
    
    # Log personalizado
    process_time = time.time() - start_time
    await log_request(request, response, process_time)
    
    return response
```

### 3. Handlers de Erro Personalizados

```python
@app.exception_handler(YourCustomException)
async def custom_exception_handler(request: Request, exc: YourCustomException):
    return templates.TemplateResponse("custom_error.html", {
        "request": request,
        "error": exc
    })
```

### 4. Integração com Ferramentas Externas

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram
REQUEST_COUNT = Counter('app_requests_total', 'Total requests')

# Integração com APM
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

## 📱 Responsividade

O dashboard é totalmente responsivo com breakpoints:

- **Desktop**: > 1024px - Layout completo com sidebar
- **Tablet**: 768px - 1024px - Layout adaptado
- **Mobile**: < 768px - Layout empilhado

### CSS Media Queries

```css
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .component-card {
        padding: 1rem;
    }
}
```

## 🔒 Segurança

### 1. Configuração de CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Especifique domínios em produção
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/")
@limiter.limit("10/minute")
async def dashboard_home(request: Request):
    # Sua lógica
```

### 3. Autenticação (Opcional)

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/")
async def dashboard_home(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verificar token
    user = verify_token(credentials.credentials)
    # Sua lógica
```

## 🚀 Deploy em Produção

### 1. Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. Nginx Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /app/static/;
        expires 1d;
    }
}
```

### 3. Systemd Service

```ini
[Unit]
Description=TecnoCursos AI Dashboard
After=network.target

[Service]
User=app
WorkingDirectory=/app
ExecStart=/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🐛 Debugging

### 1. Logs de Debug

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Em development
uvicorn main:app --log-level debug
```

### 2. JavaScript Console

```javascript
// Comandos disponíveis no console:
dashboard.toggleAutoRefresh(true/false)
dashboard.manualRefresh()
dashboardUtils.exportData()
dashboardUtils.toggleDebug()
```

### 3. Health Check Detalhado

```bash
curl http://localhost:8000/health | jq
```

## 📈 Performance

### 1. Otimizações Implementadas

- **Lazy Loading**: Componentes carregam sob demanda
- **CSS Otimizado**: Variáveis CSS e reutilização
- **JavaScript Minificado**: Em produção
- **Caching**: Headers adequados para arquivos estáticos

### 2. Monitoramento de Performance

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        
        if duration > 1.0:  # Log operações lentas
            await logging_service.log(
                LogLevel.WARNING,
                LogCategory.PERFORMANCE,
                f"Operação lenta: {func.__name__} - {duration:.2f}s"
            )
        
        return result
    return wrapper
```

## 🧪 Testes

### 1. Teste do Dashboard

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_dashboard_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "TecnoCursosAI" in response.text

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
```

### 2. Teste de Componentes

```python
def test_component_status():
    # Teste se todos os componentes estão sendo verificados
    response = client.get("/health")
    data = response.json()
    
    assert len(data["components"]) > 0
    for component in data["components"]:
        assert "name" in component
        assert "status" in component
```

## 🆘 Suporte e Troubleshooting

### Problemas Comuns

1. **404 em arquivos estáticos**
   ```bash
   # Verificar se pasta static existe
   mkdir -p static/css static/js
   ```

2. **Template não encontrado**
   ```bash
   # Verificar se pasta templates existe
   mkdir -p templates
   ```

3. **Erro de permissão em logs**
   ```bash
   # Criar pasta logs com permissões
   mkdir -p logs
   chmod 755 logs
   ```

### Logs de Diagnóstico

```python
# Ativar logs detalhados
import logging
logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logging.getLogger("fastapi").setLevel(logging.DEBUG)
```

### Contato

Para dúvidas ou problemas:
- 📧 Abra uma issue no repositório
- 📱 Consulte a documentação da API em `/docs`
- 🔍 Verifique os logs em `logs/application.log`

---

## ✅ Checklist de Implementação

- [x] ✅ Router do dashboard implementado
- [x] ✅ Template HTML responsivo criado
- [x] ✅ CSS moderno com gradientes e animações
- [x] ✅ JavaScript interativo implementado
- [x] ✅ Sistema de componentes dinâmicos
- [x] ✅ Integração com logging e notificações
- [x] ✅ Páginas de erro personalizadas (404/500)
- [x] ✅ Configuração de arquivos estáticos
- [x] ✅ Middleware de logging implementado
- [x] ✅ Health check detalhado
- [x] ✅ Documentação completa

**O dashboard está 100% funcional e pronto para customização! 🎉**

*Desenvolvido seguindo as melhores práticas de FastAPI e design moderno, com foco em performance, escalabilidade e experiência do usuário.* 