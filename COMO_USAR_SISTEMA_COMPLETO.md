# 🚀 COMO USAR O TECNOCURSOS AI - SISTEMA COMPLETO

## ✅ SISTEMA 100% FUNCIONAL - PRONTO PARA USO

O **TecnoCursos AI Enterprise Edition 2025** está completamente implementado com **todas as 6 fases concluídas**. Este guia mostra como usar cada funcionalidade.

---

## 🏁 INÍCIO RÁPIDO (30 segundos)

### **1. Iniciar o Sistema**
```bash
# Opção 1: Servidor Simplificado (recomendado para testes)
python server_simple_fase4.py

# Opção 2: Sistema Completo
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Opção 3: Monitoramento Incluído
python system/monitoring_dashboard.py  # Porta 8001
```

### **2. Acessar as Interfaces**
- 🏠 **Editor Principal:** http://localhost:8000
- 📊 **Dashboard de Monitoramento:** http://localhost:8001
- 📚 **Documentação API:** http://localhost:8000/docs
- 🔍 **Health Check:** http://localhost:8000/api/health

---

## 🎨 USANDO O EDITOR DE VÍDEOS

### **Interface Principal**
O editor possui layout profissional inspirado no Animaker:

```
┌─────────────────────────────────────────────────────────────┐
│                    TOOLBAR                                  │
│  [Novo] [Salvar] [Exportar] [Templates] [Colaborar]      │
├─────────────────────────────────────────────────────────────┤
│ ASSETS    │        CANVAS PRINCIPAL        │ CENAS         │
│           │                                │               │
│ 📚 Library│        🎨 Área de Edição      │ 📹 Lista      │
│ 🖼️ Images │                                │ ➕ Adicionar  │
│ 🎵 Audio  │        [Drop Zone]            │ 🎬 Cena 1     │
│ 🎬 Video  │                                │ 📝 Cena 2     │
│           │                                │ ✅ Cena 3     │
├─────────────────────────────────────────────────────────────┤
│                    TIMELINE                                │
│  [Play] [Pause] [Stop] | ═══════════════════════════════   │
└─────────────────────────────────────────────────────────────┘
```

### **1. Criar Novo Projeto**
```bash
# Via API
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{"name": "Meu Primeiro Vídeo", "description": "Teste do sistema"}'
```

### **2. Usar Templates Prontos**
Escolha entre 5 templates profissionais:

#### **Templates Disponíveis:**
- 🏢 **Corporativo** - Apresentações empresariais
- 🎓 **Educacional** - Aulas e tutoriais  
- 📈 **Marketing** - Promocional de produtos
- 💻 **Técnico** - Tutoriais de programação
- 📱 **Social Media** - Stories para redes sociais

```bash
# Listar templates
curl http://localhost:8000/api/templates

# Usar template
curl -X POST "http://localhost:8000/api/projects/from-template" \
  -H "Content-Type: application/json" \
  -d '{"template_id": "corporate_presentation", "project_name": "Minha Apresentação"}'
```

---

## 🎤 SISTEMA TTS (TEXT-TO-SPEECH)

### **TTS Básico**
```bash
curl -X POST "http://localhost:8000/api/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bem-vindos ao TecnoCursos AI!",
    "voice": "pt-BR",
    "speed": 1.0
  }'
```

### **TTS Avançado com Múltiplas Vozes**
```bash
# Listar vozes disponíveis
curl http://localhost:8000/api/tts/advanced/voices

# Gerar com voz premium
curl -X POST "http://localhost:8000/api/tts/advanced/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Este é um exemplo de TTS avançado",
    "voice": "pt-BR-neural",
    "effects": ["noise_reduction", "voice_enhancement"]
  }'
```

---

## 🎭 AVATARES COM IA

### **Gerar Avatar Falante**
```bash
# Listar estilos disponíveis
curl http://localhost:8000/api/avatar/styles

# Gerar avatar
curl -X POST "http://localhost:8000/api/avatar/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Olá! Eu sou seu avatar virtual.",
    "style": "professional",
    "background": "office"
  }'

# Verificar status
curl http://localhost:8000/api/avatar/status/{avatar_id}
```

### **Templates de Avatar Pré-configurados**
- 👨‍🏫 **Professor** - Ambiente de sala de aula
- 👔 **Apresentador** - Ambiente corporativo
- 🌟 **Influencer** - Ambiente moderno
- 💻 **Tech Guru** - Ambiente tecnológico

---

## 🎬 EXPORTAÇÃO DE VÍDEOS

### **Formatos Suportados**
```bash
# Ver formatos disponíveis
curl http://localhost:8000/api/video/export/formats

# Ver qualidades disponíveis  
curl http://localhost:8000/api/video/export/quality-options
```

### **Exportar Vídeo**
```bash
# Iniciar exportação
curl -X POST "http://localhost:8000/api/video/export/start" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "quality": "1080p",
    "format": "mp4"
  }'

# Acompanhar progresso
curl http://localhost:8000/api/video/export/status/{job_id}
```

### **Opções de Qualidade**
- 📺 **720p HD** - Para web e mobile
- 🖥️ **1080p Full HD** - Para desktop e TV
- 🎯 **4K UHD** - Para produção profissional

---

## 🤝 COLABORAÇÃO EM TEMPO REAL

### **Iniciar Sessão Colaborativa**
```javascript
// Conectar via WebSocket
const ws = new WebSocket('ws://localhost:8000/api/collaboration/session123');

ws.onopen = function() {
    // Entrar na sessão
    ws.send(JSON.stringify({
        type: 'join_session',
        user: {
            id: 'user123',
            name: 'João Silva',
            permission: 'editor'
        }
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Evento colaborativo:', data);
};
```

### **Funcionalidades Colaborativas**
- 👥 **Multi-usuário** - Até 50 usuários simultâneos
- 🖱️ **Live Cursors** - Ver cursors de outros usuários em tempo real
- 💬 **Comentários** - Adicionar comentários em elementos
- 🔒 **Bloqueio** - Bloquear projeto para edição exclusiva
- 📝 **Histórico** - Ver todas as ações realizadas

---

## 📊 ANALYTICS E MONITORAMENTO

### **Dashboard de Analytics**
Acesse: http://localhost:8001

#### **Métricas Disponíveis:**
- 💻 **CPU/Memory Usage** - Performance do sistema
- 👥 **Usuários Ativos** - Usuários online
- 🎬 **Vídeos Gerados** - Estatísticas de produção
- ⚡ **Response Time** - Tempo de resposta
- 🚨 **Alertas** - Problemas detectados

### **APIs de Analytics**
```bash
# Métricas atuais
curl http://localhost:8000/api/analytics/current

# Histórico de usuário
curl http://localhost:8000/api/analytics/user/user123

# Relatório diário
curl http://localhost:8000/api/analytics/daily-report
```

---

## 🔔 SISTEMA DE NOTIFICAÇÕES

### **WebSocket Real-time**
```javascript
const notificationWs = new WebSocket('ws://localhost:8000/api/notifications/ws/user123');

notificationWs.onmessage = function(event) {
    const notification = JSON.parse(event.data);
    
    // Exibir notificação
    showNotification(notification.title, notification.message);
};
```

### **API REST de Notificações**
```bash
# Enviar notificação
curl -X POST "http://localhost:8000/api/notifications/send" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Seu vídeo foi processado com sucesso!",
    "type": "success"
  }'

# Listar notificações
curl http://localhost:8000/api/notifications/user123
```

---

## 🧪 TESTES AUTOMATIZADOS

### **Executar Testes das Fases**
```bash
# Teste da Fase 4 (Integrações)
python test_fase_4_completo.py

# Teste da Fase 5 (Performance)
python tests/test_fase_5_completo.py

# Todos os testes
python -m pytest tests/ -v
```

### **Resultados Esperados**
- ✅ **Taxa de Sucesso:** 90%+
- ✅ **Response Time:** <2s
- ✅ **Concorrência:** 50+ usuários simultâneos
- ✅ **Segurança:** Proteção XSS/SQL Injection

---

## 🔧 CONFIGURAÇÃO AVANÇADA

### **Variáveis de Ambiente**
```bash
# Copiar configuração
cp .env.example .env

# Configurações importantes
DATABASE_URL=sqlite:///./tecnocursos.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=sua-chave-secreta-aqui

# APIs externas (opcional)
D_ID_API_KEY=sua-chave-d-id
SYNTHESIA_API_KEY=sua-chave-synthesia
```

### **Performance Optimization**
```bash
# Iniciar otimizador de performance
python system/performance_optimizer.py

# Configurar Redis para cache
redis-server --port 6379

# Iniciar monitoring
python system/monitoring_dashboard.py
```

---

## 🚀 DEPLOYMENT EM PRODUÇÃO

### **Docker Compose**
```bash
# Produção com Docker
docker-compose -f docker-compose.production.yml up -d

# Verificar status
docker-compose ps
docker-compose logs -f
```

### **Kubernetes**
```bash
# Deploy em Kubernetes
kubectl apply -f k8s/production/

# Verificar pods
kubectl get pods -n tecnocursos
kubectl logs -f deployment/tecnocursos-api
```

---

## 📚 RECURSOS ADICIONAIS

### **Documentação Técnica**
- 📖 **API Docs:** http://localhost:8000/docs
- 📋 **ReDoc:** http://localhost:8000/redoc
- 🔍 **Status:** http://localhost:8000/api/health

### **Exemplos de Integração**
```python
# Cliente Python
import requests

# Criar projeto
response = requests.post('http://localhost:8000/api/projects', json={
    'name': 'Projeto via API',
    'description': 'Criado programaticamente'
})

project = response.json()
print(f"Projeto criado: {project['id']}")

# Gerar vídeo
video_response = requests.post('http://localhost:8000/api/video/generate', json={
    'project_id': project['id'],
    'include_narration': True,
    'include_avatar': True
})
```

---

## 🆘 SUPORTE E TROUBLESHOOTING

### **Problemas Comuns**

#### **1. Servidor não inicia**
```bash
# Verificar dependências
pip install -r requirements.txt

# Testar importações
python -c "from app.main import app; print('✅ OK')"

# Verificar porta
netstat -ano | findstr :8000
```

#### **2. Redis não conecta**
```bash
# Instalar Redis
# Windows: https://redis.io/download
# Linux: sudo apt install redis-server

# Testar conexão
redis-cli ping
```

#### **3. Performance lenta**
```bash
# Verificar recursos
python system/performance_optimizer.py

# Ver métricas
curl http://localhost:8001/api/metrics/current
```

### **Logs do Sistema**
```bash
# Ver logs em tempo real
tail -f logs/app.log

# Logs específicos
grep "ERROR" logs/app.log
grep "performance" logs/optimization_actions.json
```

---

## 🎉 CONCLUSÃO

O **TecnoCursos AI** está **100% implementado e funcional**, oferecendo:

### ✅ **Funcionalidades Completas**
- **Editor Visual** - Drag & drop profissional
- **Templates Prontos** - 5 categorias otimizadas
- **IA Integrada** - TTS, avatares, sugestões
- **Colaboração Real-time** - Multi-usuário
- **Analytics Avançado** - Métricas e relatórios
- **Performance Enterprise** - Monitoramento automático

### 🚀 **Pronto para Uso**
O sistema está pronto para:
- **Desenvolvimento** - Ambiente local completo
- **Teste** - Suíte de testes automatizados
- **Produção** - Configuração enterprise
- **Escala** - Suporte a milhares de usuários

### 💡 **Próximos Passos**
1. **Explore as funcionalidades** seguindo este guia
2. **Execute os testes** para validar o ambiente
3. **Configure para produção** quando estiver pronto
4. **Monitore a performance** com o dashboard

---

**🎯 TecnoCursos AI Enterprise Edition 2025 - O futuro da educação digital!**

*Sistema 100% funcional e pronto para revolucionar a criação de conteúdo educacional.* 