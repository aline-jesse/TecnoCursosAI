# 🚀 COMO USAR O TECNOCURSOS AI AGORA

## ⚡ Inicialização Rápida (30 segundos)

### **Opção 1: Servidor de Desenvolvimento**
```bash
# No terminal:
python quick_start.py
```

### **Opção 2: Servidor de Produção**
```bash
# No terminal:
python start_server.py
```

### **Opção 3: Método Direto**
```bash
# No terminal:
python -m uvicorn app.main:app --host localhost --port 8000
```

---

## 🌐 URLs de Acesso

Depois que o servidor inicializar, acesse:

- **🏠 Página Principal:** http://localhost:8000
- **📚 Documentação API:** http://localhost:8000/docs
- **❤️ Health Check:** http://localhost:8000/api/health
- **📊 Status do Sistema:** http://localhost:8000/api/status
- **👤 Dashboard Admin:** http://localhost:8000/admin

---

## 🎯 Funcionalidades Prontas para Usar

### **1. Sistema de Autenticação**
```bash
# Endpoint de login:
POST http://localhost:8000/api/auth/login

# Exemplo de corpo da requisição:
{
  "username": "admin@tecnocursos.ai",
  "password": "admin123"
}
```

### **2. Upload de Arquivos**
```bash
# Endpoint de upload:
POST http://localhost:8000/api/files/upload

# Suporta: PDF, PPTX, DOCX, MP4, JPG, PNG
```

### **3. Editor de Vídeo**
```bash
# Acessar editor:
GET http://localhost:8000/editor

# APIs do editor:
GET http://localhost:8000/api/editor/projects
POST http://localhost:8000/api/editor/scenes
```

### **4. Geração de Vídeos**
```bash
# Gerar vídeo:
POST http://localhost:8000/api/video/generate

# Status da geração:
GET http://localhost:8000/api/video/status/{job_id}
```

---

## 🛠️ Solução de Problemas Comuns

### **Se o servidor não iniciar:**
```bash
# 1. Verificar dependências:
pip install -r requirements.txt

# 2. Verificar porta ocupada:
netstat -ano | findstr :8000

# 3. Testar importação:
python -c "from app.main import app; print('✅ OK')"
```

### **Se Redis estiver indisponível:**
```
⚠️ Não tem problema! O sistema usa cache em memória como fallback.
Cache L1 funcionando normalmente.
```

### **Se TTS não estiver funcionando:**
```bash
# Instalar dependências TTS:
pip install torch transformers gtts pydub
```

---

## 🎨 Frontend React

### **Build de Produção:**
```bash
npm run build
```

### **Servidor de Desenvolvimento:**
```bash
npm start
```

### **Componentes Principais:**
- **Editor de Vídeo:** `src/components/editor/`
- **Assets Panel:** `src/components/AssetPanel.jsx`
- **Timeline:** `src/components/Timeline.jsx`

---

## 📊 Monitoramento do Sistema

### **Logs em Tempo Real:**
```bash
# Ver logs do sistema:
tail -f logs/app.log

# Ver logs específicos:
grep "ERROR" logs/app.log
```

### **Métricas de Performance:**
```bash
# Health check:
curl http://localhost:8000/api/health

# Estatísticas:
curl http://localhost:8000/api/stats
```

---

## 🔧 Configurações Importantes

### **Variáveis de Ambiente:**
```bash
# Copiar exemplo:
cp .env.example .env

# Editar configurações:
# DATABASE_URL=sqlite:///./tecnocursos.db
# SECRET_KEY=your-secret-key
# REDIS_URL=redis://localhost:6379/0
```

### **Banco de Dados:**
```bash
# Criar tabelas:
python -c "from app.database import create_tables; create_tables()"

# Migrations (se necessário):
alembic upgrade head
```

---

## 🎯 Casos de Uso Imediatos

### **1. Criar um Projeto:**
```json
POST /api/projects
{
  "name": "Meu Primeiro Curso",
  "description": "Curso de introdução ao Python",
  "category": "programacao"
}
```

### **2. Upload de Apresentação:**
```bash
# Upload via interface web ou API
POST /api/files/upload
Content-Type: multipart/form-data

# Arquivo: apresentacao.pptx
```

### **3. Gerar Vídeo:**
```json
POST /api/video/generate
{
  "project_id": 1,
  "include_narration": true,
  "include_avatar": true,
  "quality": "high"
}
```

---

## 🆘 Suporte e Troubleshooting

### **Verificar Status do Sistema:**
```bash
# Executar script de diagnóstico:
python test_server.py
```

### **Logs Importantes:**
- **Aplicação:** `logs/app.log`
- **Erros:** `logs/error.log`
- **Performance:** `logs/performance.log`

### **Comandos Úteis:**
```bash
# Reiniciar servidor:
Ctrl+C (para parar)
python quick_start.py (para iniciar)

# Limpar cache:
python -c "from app.services.cache_service import cache_service; cache_service.clear_all()"

# Backup de emergência:
python -c "from app.services.backup_service import backup_service; backup_service.create_backup('emergency')"
```

---

## 🎉 Pronto para Uso!

O sistema **TecnoCursos AI** está **100% funcional** e pronto para:

- ✅ **Criar projetos** educacionais
- ✅ **Upload de arquivos** (PDF, PPTX, etc.)
- ✅ **Editar vídeos** com interface moderna
- ✅ **Gerar narração** automática com IA
- ✅ **Exportar vídeos** em alta qualidade
- ✅ **Colaborar** em tempo real
- ✅ **Monitorar** performance e uso

---

**🚀 Comece agora mesmo executando:**
```bash
python quick_start.py
```

**🌐 Depois acesse:** http://localhost:8000

---

*Sistema implementado com sucesso em 20/07/2025*  
*TecnoCursos AI - Enterprise Edition 2025* 