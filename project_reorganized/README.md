# 🚀 TecnoCursos AI - Sistema Reorganizado e Funcional

## 📋 Visão Geral

O TecnoCursos AI foi reorganizado em uma estrutura limpa e modular para facilitar desenvolvimento, manutenção e deploy.

## 🏗️ Nova Estrutura Organizacional

```
TecnoCursosAI/
├── backend/                 # Backend FastAPI
│   ├── app/                # Aplicação principal
│   │   ├── core/           # Configurações core
│   │   ├── routers/        # Endpoints da API
│   │   ├── services/       # Lógica de negócio
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Esquemas Pydantic
│   │   ├── middleware/     # Middlewares personalizados
│   │   └── security/       # Segurança e autenticação
│   ├── config/             # Configurações de ambiente
│   ├── data/               # Dados de aplicação
│   ├── scripts/            # Scripts de backend
│   └── tests/              # Testes do backend
├── frontend/               # Frontend React
│   ├── src/                # Código fonte
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas/Views
│   │   ├── services/       # Serviços API
│   │   ├── hooks/          # Custom hooks
│   │   ├── types/          # Tipos TypeScript
│   │   ├── store/          # Estado global
│   │   ├── styles/         # Estilos CSS
│   │   └── utils/          # Utilitários
│   ├── public/             # Arquivos públicos
│   └── tests/              # Testes do frontend
├── tools/                  # Ferramentas e scripts
│   ├── scripts/            # Scripts organizados
│   │   ├── dev/            # Scripts de desenvolvimento
│   │   ├── prod/           # Scripts de produção
│   │   ├── testing/        # Scripts de teste
│   │   └── deployment/     # Scripts de deploy
│   ├── automation/         # Automação e CI/CD
│   └── monitoring/         # Monitoramento
├── infrastructure/         # Infraestrutura como código
│   ├── docker/             # Configurações Docker
│   ├── kubernetes/         # Manifestos K8s
│   ├── nginx/              # Configurações Nginx
│   └── terraform/          # Scripts Terraform
├── docs/                   # Documentação
│   ├── api/                # Documentação da API
│   ├── user/               # Manual do usuário
│   └── developer/          # Guia de desenvolvedor
└── deployment/             # Scripts e configs de deploy
```

## 🚀 Início Rápido

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm start
```

### 3. Sistema Completo
```bash
python tools/scripts/dev/start_development.py
```

## 🔧 Principais Melhorias

- ✅ **Estrutura organizada** - Separação clara de responsabilidades
- ✅ **Dependências consolidadas** - Fim de requirements duplicados
- ✅ **Scripts organizados** - Categorizados por função
- ✅ **Configuração centralizada** - Ambiente único
- ✅ **Documentação estruturada** - Categorizada por público
- ✅ **Infraestrutura como código** - Deploy automatizado
- ✅ **Monitoramento integrado** - Observabilidade completa

## 📚 Documentação

- [Guia de Instalação](docs/user/installation.md)
- [API Reference](docs/api/README.md)
- [Guia do Desenvolvedor](docs/developer/README.md)

## 🤝 Contribuição

Ver [CONTRIBUTING.md](docs/developer/CONTRIBUTING.md) para guidelines de contribuição.

## 📄 Licença

MIT License - ver [LICENSE](LICENSE) para detalhes. 