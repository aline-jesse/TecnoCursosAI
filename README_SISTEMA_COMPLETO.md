# 🚀 TecnoCursosAI - Sistema Completo de Criação de Vídeos com IA

## 📋 Visão Geral

O **TecnoCursosAI** é uma plataforma enterprise completa para criação de vídeos educacionais com IA, similar ao Animaker mas com recursos avançados de inteligência artificial, processamento quântico e edge computing.

## ✨ Funcionalidades Principais

### 🎬 Editor de Vídeos
- Canvas interativo com Fabric.js
- Drag & drop de elementos
- Timeline avançado
- Biblioteca de assets
- Templates prontos
- Exportação em múltiplos formatos

### 🤖 IA Avançada
- Text-to-Speech (TTS) com múltiplas vozes
- Geração de avatares digitais
- Processamento de linguagem natural
- IA multimodal
- Prompt engineering avançado

### 🔬 Recursos Enterprise
- Computação quântica para otimização
- Edge computing distribuído
- Analytics em tempo real
- Sistema de backup automático
- Monitoramento inteligente
- APIs RESTful completas

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.13** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy 2.0** - ORM para banco de dados
- **Redis** - Cache e mensageria
- **WebSockets** - Comunicação em tempo real

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Zustand** - Gerenciamento de estado
- **Fabric.js** - Canvas interativo
- **TailwindCSS** - Estilização

## 📦 Instalação Rápida

### Pré-requisitos
- Python 3.13 ou superior
- Node.js 18 ou superior
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/TecnoCursosAI.git
cd TecnoCursosAI
```

### 2. Inicie o sistema completo
```bash
# Windows
start_complete_system.bat

# Linux/Mac
./start_complete_system.sh
```

## 🚀 Inicialização Manual

### Backend
```bash
# Instalar dependências
pip install -r backend/requirements_fixed.txt

# Iniciar servidor
python start_production_server.py
```

### Frontend
```bash
# Navegar para o diretório
cd frontend

# Instalar dependências
npm install

# Iniciar aplicação
npm start
```

## 🌐 URLs do Sistema

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API (Swagger)**: http://localhost:8000/docs
- **Documentação API (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 📚 Estrutura do Projeto

```
TecnoCursosAI/
├── backend/              # Servidor FastAPI
│   ├── app/             # Aplicação principal
│   ├── services/        # Serviços de IA e processamento
│   ├── routers/         # Endpoints da API
│   └── tests/           # Testes unitários
├── frontend/            # Aplicação React
│   ├── src/            # Código fonte
│   ├── components/     # Componentes React
│   └── public/         # Assets públicos
├── docs/               # Documentação
├── scripts/            # Scripts utilitários
└── docker/             # Configuração Docker
```

## 🔧 Principais APIs

### Vídeo e Mídia
- `POST /api/video/generate` - Gerar vídeo com IA
- `POST /api/tts/generate` - Converter texto em áudio
- `POST /api/avatar/generate` - Criar avatar digital

### Editor
- `GET /api/scenes` - Listar cenas
- `POST /api/scenes` - Criar nova cena
- `PUT /api/scenes/{id}` - Atualizar cena
- `DELETE /api/scenes/{id}` - Deletar cena

### Assets
- `GET /api/assets` - Listar assets
- `POST /api/assets/upload` - Upload de arquivo
- `GET /api/assets/{id}` - Baixar asset

### IA Avançada
- `POST /api/modern-ai/prompt` - Processamento com IA
- `POST /api/quantum/optimize` - Otimização quântica
- `GET /api/edge/nodes` - Status dos nós edge

## 💡 Exemplos de Uso

### Gerar Áudio TTS
```python
import requests

response = requests.post("http://localhost:8000/api/tts/generate", 
    json={
        "text": "Olá, bem-vindo ao TecnoCursosAI!",
        "voice": "pt-BR-AntonioNeural",
        "speed": 1.0
    }
)
```

### Criar Nova Cena
```javascript
fetch("http://localhost:8000/api/scenes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        title: "Minha Cena",
        duration: 10,
        elements: []
    })
})
```

## 🧪 Testes

### Backend
```bash
cd backend
pytest tests/
```

### Frontend
```bash
cd frontend
npm test
```

## 🐛 Solução de Problemas

### Porta já em uso
```bash
# Windows - Encontrar processo usando a porta
netstat -ano | findstr :8000

# Matar processo
taskkill /PID <PID> /F
```

### Dependências faltando
```bash
# Backend
pip install -r backend/requirements_production.txt

# Frontend
cd frontend && npm install
```

### Erro de CORS
Verifique se o backend está configurado com as origens corretas em `backend/app/main.py`

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

- Email: suporte@tecnocursosai.com
- Discord: [TecnoCursosAI Community](https://discord.gg/tecnocursos)
- Documentação: [docs.tecnocursosai.com](https://docs.tecnocursosai.com)

## 🎉 Status do Sistema

✅ **Backend**: Funcionando (60+ endpoints)
✅ **Frontend**: Funcionando (React + TypeScript)
✅ **Banco de Dados**: SQLite (dev) / PostgreSQL (prod)
✅ **Cache**: Redis com fallback
✅ **IA**: Modern AI, Quantum, Edge Computing

---

**Desenvolvido com ❤️ pela equipe TecnoCursosAI** 