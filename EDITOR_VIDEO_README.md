# 🎬 Editor de Vídeo TecnoCursos AI

## Visão Geral

O Editor de Vídeo TecnoCursos AI é uma solução completa de edição de vídeo baseada na web, integrada ao sistema educacional TecnoCursos AI. Oferece uma interface moderna e intuitiva para criação e edição de conteúdo audiovisual.

## 🚀 Funcionalidades

### Interface do Editor
- **Timeline Multi-track**: Suporte a múltiplas camadas de vídeo, áudio e efeitos
- **Preview em Tempo Real**: Visualização instantânea das edições
- **Biblioteca de Mídia**: Gerenciamento organizado de assets
- **Painel de Propriedades**: Controles avançados para clips selecionados
- **Ferramentas de Transformação**: Posição, rotação, escala e opacidade

### Recursos de Edição
- **Corte e Divisão**: Ferramentas precisas de corte
- **Arrastar e Soltar**: Interface intuitiva para organização
- **Efeitos Visuais**: Filtros, brightness, contraste, saturação
- **Mixagem de Áudio**: Controle de volume e fade
- **Texto e Legendas**: Sobreposições de texto personalizáveis
- **Transições**: Efeitos suaves entre clips

### Processamento Backend
- **FFmpeg Integration**: Processamento profissional de vídeo
- **Múltiplos Formatos**: MP4, MOV, AVI, WebM
- **Qualidade Configurável**: Low, Medium, High, Ultra
- **Processamento Assíncrono**: Exportação em background
- **Monitoramento**: Progresso em tempo real

## 📋 Pré-requisitos

### Sistema
- **Sistema Operacional**: Windows 10+, macOS 10.14+, ou Linux Ubuntu 18.04+
- **Memória RAM**: Mínimo 8GB (recomendado 16GB+)
- **Espaço em Disco**: 5GB para instalação + espaço para projetos
- **Processador**: Intel i5 ou AMD Ryzen 5 (mínimo)

### Software
- **Python**: 3.8 ou superior
- **Node.js**: 16.0 ou superior
- **FFmpeg**: Versão mais recente
- **Redis**: Para cache (opcional)
- **PostgreSQL**: Para banco de dados

## 🛠️ Instalação

### Instalação Automática

```bash
# Clonar o repositório
git clone <repository-url>
cd TecnoCursosAI

# Executar instalação automática
python start_video_editor.py
```

### Instalação Manual

#### 1. Backend
```bash
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements_video.txt

# Configurar banco de dados
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

#### 3. FFmpeg
**Windows:**
1. Baixar de https://ffmpeg.org/download.html
2. Extrair para C:\ffmpeg
3. Adicionar C:\ffmpeg\bin ao PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🎯 Como Usar

### 1. Inicialização
1. Execute `python start_video_editor.py`
2. Aguarde a inicialização dos serviços
3. Acesse http://localhost:3000

### 2. Criando um Projeto
1. Clique em "Novo Projeto"
2. Configure nome e configurações (resolução, frame rate)
3. Comece a adicionar mídia

### 3. Importando Mídia
- Arraste arquivos para a área de upload
- Ou clique em "Importar Mídia"
- Formatos suportados: MP4, MOV, AVI, MP3, WAV, JPG, PNG

### 4. Editando no Timeline
- Arraste mídia da biblioteca para o timeline
- Use ferramentas de corte (C) para dividir clips
- Redimensione clips arrastando as bordas
- Mova clips entre camadas

### 5. Aplicando Efeitos
1. Selecione um clip
2. Use o painel de propriedades
3. Ajuste parâmetros em tempo real
4. Visualize no preview

### 6. Exportando
1. Clique em "Exportar"
2. Escolha formato e qualidade
3. Aguarde o processamento
4. Download automático ao concluir

## ⌨️ Atalhos de Teclado

| Ação | Atalho |
|------|--------|
| Play/Pause | Barra de Espaço |
| Salvar Projeto | Ctrl+S |
| Desfazer | Ctrl+Z |
| Refazer | Ctrl+Shift+Z |
| Cortar Clip | C |
| Duplicar Clip | Ctrl+D |
| Deletar Clip | Delete |
| Zoom In Timeline | + |
| Zoom Out Timeline | - |

## 🔧 Configurações Avançadas

### Variáveis de Ambiente
```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost/tecnocursos
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
UPLOAD_MAX_SIZE=500MB

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAX_FILE_SIZE=500000000
```

### Configuração de Qualidade
```python
# backend/app/core/settings.py
VIDEO_QUALITY_PRESETS = {
    "low": {"bitrate": "1M", "crf": 28},
    "medium": {"bitrate": "2M", "crf": 23},
    "high": {"bitrate": "4M", "crf": 18},
    "ultra": {"bitrate": "8M", "crf": 15}
}
```

## 📊 Monitoramento

### Logs
- **Backend**: `logs/backend.log`
- **Frontend**: Console do navegador
- **FFmpeg**: `logs/ffmpeg.log`

### Métricas
- Tempo de processamento
- Uso de memória
- Taxa de erro
- Throughput de uploads

## 🔒 Segurança

### Validação de Arquivos
- Verificação de tipo MIME
- Limite de tamanho
- Sanitização de nomes
- Validação de conteúdo

### Autenticação
- JWT tokens
- Rate limiting
- CORS configurado
- Validação de entrada

## 🐛 Solução de Problemas

### Problemas Comuns

**Erro: FFmpeg não encontrado**
```bash
# Verificar instalação
ffmpeg -version

# Reinstalar se necessário
# Windows: Baixar e adicionar ao PATH
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

**Erro: Falha no upload**
- Verificar tamanho do arquivo (máx 500MB)
- Confirmar formato suportado
- Verificar espaço em disco

**Erro: Processamento lento**
- Verificar recursos do sistema
- Reduzir qualidade de export
- Fechar aplicações desnecessárias

**Erro: Preview não funciona**
- Verificar codec do vídeo
- Atualizar navegador
- Verificar configurações de hardware

### Debug Mode
```bash
# Backend com debug
uvicorn app.main:app --reload --log-level debug

# Frontend com debug
npm run dev -- --inspect
```

## 📈 Performance

### Otimizações Recomendadas
1. **SSD**: Use SSD para arquivos temporários
2. **RAM**: 16GB+ para projetos grandes
3. **GPU**: Aceleração por hardware (opcional)
4. **Network**: Conexão estável para uploads

### Configurações de Performance
```python
# backend/config.py
FFMPEG_THREADS = 4  # Número de threads
MAX_CONCURRENT_EXPORTS = 2  # Exports simultâneos
CACHE_TTL = 3600  # TTL do cache
```

## 🔄 Atualizações

### Verificar Versão
```bash
python --version
node --version
ffmpeg -version
```

### Atualizar Dependências
```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
npm update
```

## 📞 Suporte

### Documentação
- **API**: http://localhost:8000/docs
- **Código**: Comentários inline
- **README**: Arquivos específicos por módulo

### Contato
- **Issues**: GitHub Issues
- **Email**: suporte@tecnocursos.ai
- **Discord**: [Link do servidor]

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

**Desenvolvido com ❤️ pela equipe TecnoCursos AI**
