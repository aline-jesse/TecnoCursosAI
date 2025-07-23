# 🚀 Backend FastAPI - TecnoCursosAI

## Sumário
- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Instalação e Inicialização](#instalação-e-inicialização)
- [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
- [Seed de Dados](#seed-de-dados)
- [Principais Endpoints](#principais-endpoints)
- [Exemplos de Uso](#exemplos-de-uso)
- [Testes Automatizados](#testes-automatizados)
- [Deploy e Produção](#deploy-e-produção)
- [Documentação Swagger/OpenAPI](#documentação-swaggeropenapi)

---

## Visão Geral
Backend completo para o sistema TecnoCursosAI, implementado em FastAPI, com suporte a:
- CRUD de projetos, cenas e assets
- Upload de arquivos (PDF, PPTX, imagens, áudio, vídeo)
- Importação automática de slides e criação de cenas
- Exportação de vídeo MP4 unindo cenas, slides, áudio e assets (MoviePy)
- Banco de dados MySQL (compatível com SQLite para testes)
- Dashboard customizado, health check, status e documentação automática
- Testes automatizados (Pytest)

---

## Funcionalidades
- **CRUD completo**: projetos, cenas, assets, usuários
- **Upload seguro**: PDF, PPTX, imagens, áudio, vídeo
- **Importação de slides**: extração de slides de PDF/PPTX, criação automática de cenas
- **Exportação de vídeo**: pipeline MoviePy, TTS, assets, transições, download MP4
- **Dashboard**: status do sistema, links úteis, health check
- **Documentação automática**: Swagger/OpenAPI
- **Testes automatizados**: cobertura Pytest, integração e carga

---

## Estrutura de Pastas
```
app/
  routers/         # Endpoints (projetos, cenas, assets, upload, exportação, dashboard)
  models.py        # Modelos SQLAlchemy
  schemas.py       # Schemas Pydantic
  services/        # Serviços auxiliares (vídeo, assets, etc)
  utils.py         # Funções utilitárias
  database.py      # Conexão e inicialização do banco
  static/          # Arquivos enviados e gerados
  templates/       # Templates HTML (dashboard)
tests/             # Testes automatizados (Pytest)
```

---

## Instalação e Inicialização
```bash
# 1. Clone o repositório
$ git clone <repo_url>
$ cd TecnoCursosAI

# 2. Crie e ative o ambiente virtual
$ python3 -m venv venv
$ source venv/bin/activate  # Linux/Mac
$ venv\Scripts\activate    # Windows

# 3. Instale as dependências
$ pip install -r requirements.txt

# 4. Configure o banco de dados (MySQL ou SQLite)
# Edite app/config.py conforme necessário

# 5. Inicialize o banco
$ python app/database.py

# 6. Rode o servidor
$ uvicorn app.main:app --reload
```

---

## Configuração do Banco de Dados
- Por padrão, usa SQLite para testes.
- Para produção, configure MySQL em `app/config.py`:
  ```python
  SQLALCHEMY_DATABASE_URL = "mysql+pymysql://usuario:senha@localhost:3306/tecnocursosai"
  ```
- Execute as migrações ou inicialize com o script fornecido.

---

## Seed de Dados
- Script de seed: `scripts/seed_data.py`
- Popula usuários admin, projetos, cenas e assets de exemplo.
```bash
$ python scripts/seed_data.py
```

---

## Principais Endpoints
- **Dashboard:** `GET /`
  HTML+CSS com status do sistema, funcionalidades e links úteis
- **Projetos:** `GET/POST /api/projects`
  CRUD completo de projetos
- **Cenas:** `GET/POST /api/scenes`
  CRUD completo de cenas
- **Assets:** `GET/POST /api/assets`
  CRUD completo de assets
- **Upload de Arquivos:** `POST /files/upload`
  Upload de PDF, PPTX, imagens, áudio, vídeo
- **Importação de Slides:** `POST /advanced-video/extract-pdf-slides`
  Extrai slides de PDF como imagens
- **Exportação de Vídeo:** `POST /video-export/export`
  Gera vídeo MP4 unindo cenas, slides, áudio e assets
- **Exportação de Vídeo com IA:** `POST /export-ia`
  Exportação de vídeo com IA, TTS e avatar
- **Health Check:** `GET /api/health`
- **Documentação:** `GET /docs` (Swagger), `GET /redoc`

---

## Exemplos de Uso
### Upload de Arquivo PDF
```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@/caminho/arquivo.pdf" \
  -F "project_id=1"
```

### Importação de Slides de PDF
```bash
curl -X POST "http://localhost:8000/advanced-video/extract-pdf-slides" \
  -F "pdf_file=@/caminho/arquivo.pdf" \
  -F "request_data={\"dpi\":150,\"image_format\":\"PNG\"}"
```

### Exportação de Vídeo
```bash
curl -X POST "http://localhost:8000/video-export/export" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Meu Vídeo", "scenes": [...], "resolution": "1080p", "quality": "high"}'
```

### Exportação de Vídeo com IA

### Endpoint síncrono
`POST /export-ia`

### Endpoint assíncrono (recomendado para vídeos longos)
`POST /export-ia-async`

#### Parâmetros:
- `project_id` (int): ID do projeto a ser exportado
- `tts_model` (str, opcional): Modelo TTS a ser usado (`coqui` ou `bark`). Default: `coqui`
- `avatar_model` (str, opcional): Modelo de avatar IA (`hunyuan3d2` ou outro). Default: `hunyuan3d2`

#### Exemplo de requisição assíncrona:
```bash
curl -X POST "http://localhost:8001/api/export-ia-async" \
  -H "accept: application/json" \
  -H "Authorization: Bearer <token>" \
  -d "project_id=1&tts_model=coqui&avatar_model=hunyuan3d2"
```

#### Resposta:
```json
{
  "success": true,
  "video_id": null,
  "message": "Exportação IA agendada em background. Você será notificado ao finalizar.",
  "data": {
    "project_id": 1
  }
}
```

> **Nota:** Para vídeos longos, utilize o endpoint assíncrono `/export-ia-async` para não bloquear a requisição. O processamento ocorre em background e o vídeo será salvo e associado ao projeto ao final.

### Consultar status da exportação IA
`GET /export-ia-status/{project_id}`

- Retorna status da última exportação IA do projeto.
- Se concluído, retorna link para download do vídeo.

#### Exemplo de resposta:
```json
{
  "status": "completed",
  "download_url": "/static/videos/generated/project_1/final_project_video.mp4"
}
```

### Troca de modelo TTS/Avatar
- Para alterar o modelo padrão de TTS ou avatar, defina as variáveis de ambiente:
  - `TTS_MODEL=coqui` ou `TTS_MODEL=bark`
  - `AVATAR_MODEL=hunyuan3d2` (ou outro)
- Também é possível passar o modelo desejado diretamente na requisição.

### Modularidade e Logs
- O pipeline IA é totalmente modular: basta alterar o modelo ou função para atualizar a IA.
- Logs detalhados são gerados em cada etapa do pipeline para facilitar rastreamento e depuração.

---

## Importação automática de apresentações PDF/PPTX

### Endpoint
`POST /import-presentations/`

- Permite upload de múltiplos arquivos PDF e PPTX associados a um projeto.
- Para cada slide/página, extrai texto e imagens e cria uma nova cena no projeto.
- Retorna preview imediato das cenas para o front-end.

#### Parâmetros:
- `project_id` (form): ID do projeto
- `files` (form): Arquivos PDF e/ou PPTX (multi-arquivo)

#### Exemplo de requisição (cURL):
```bash
curl -X POST "http://localhost:8001/api/import-presentations/" \
  -F "project_id=1" \
  -F "files=@/caminho/arquivo1.pdf" \
  -F "files=@/caminho/arquivo2.pptx"
```

#### Resposta:
```json
{
  "success": true,
  "created_scenes": [
    {
      "scene_id": 123,
      "name": "arquivo1.pdf - Slide 1",
      "texto": "Texto extraído do slide",
      "imagens": ["/static/uploads/slides/project_1_arquivo1/slide_1_img_1.png"]
    },
    ...
  ]
}
```

### Como adicionar novos formatos
- Crie um novo arquivo em `app/parsers/` seguindo o padrão `parse_<formato>(file_path, output_dir) -> List[Dict]`.
- Importe e registre o parser em `app/parsers/__init__.py`.
- Adapte o endpoint para reconhecer a nova extensão e chamar o parser correspondente.

### Listar formatos suportados para importação
`GET /import-supported-formats/`

- Retorna as extensões de arquivo atualmente suportadas para importação automática de apresentações.

#### Exemplo de resposta:
```json
{
  "supported_formats": [".pdf", ".pptx"]
}
```

---

## Testes Automatizados
- Execute todos os testes com:
```bash
$ pytest tests/
```
- Testes de integração, unidade, carga e performance.

---

## Deploy e Produção
- Recomenda-se uso de Uvicorn + Gunicorn + Nginx
- Exemplo:
```bash
$ uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- Para deploy automatizado, utilize GitHub Actions, Docker ou scripts fornecidos.

---

## Documentação Swagger/OpenAPI
- Acesse: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

**Dúvidas? Consulte a documentação, exemplos e scripts no repositório.**

---

**Status Final:**
- Backend FastAPI 100% funcional, testado, documentado e pronto para produção.

> **Notificação:** Ao finalizar a exportação IA, o sistema envia automaticamente um e-mail para o proprietário do projeto (se o e-mail estiver cadastrado), informando que o vídeo está pronto para download.
