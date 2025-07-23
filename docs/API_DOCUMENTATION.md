# Documentação da API - TecnoCursosAI

## Visão Geral

A API TecnoCursosAI é uma aplicação FastAPI que fornece funcionalidades para:
- Upload e processamento de arquivos (PDF, PPTX)
- Geração de vídeos com IA
- Sistema de autenticação e usuários
- Geração de áudio com TTS
- Criação de avatares e vídeos personalizados

## Base URL

```
http://localhost:8000
```

## Autenticação

A API usa JWT (JSON Web Tokens) para autenticação.

### Endpoints de Autenticação

#### POST /auth/register
Registra um novo usuário.

**Request Body:**
```json
{
  "username": "usuario@exemplo.com",
  "password": "senha123",
  "confirm_password": "senha123"
}
```

**Response:**
```json
{
  "message": "Usuário criado com sucesso",
  "user_id": 1
}
```

#### POST /auth/login
Faz login do usuário.

**Request Body:**
```json
{
  "username": "usuario@exemplo.com",
  "password": "senha123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "usuario@exemplo.com"
  }
}
```

## Endpoints de Upload

### POST /upload/
Faz upload de arquivos (PDF, PPTX).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```
multipart/form-data
- file: arquivo.pdf ou arquivo.pptx
```

**Response:**
```json
{
  "filename": "arquivo.pdf",
  "file_id": "uuid-123",
  "status": "uploaded",
  "message": "Arquivo enviado com sucesso"
}
```

## Endpoints de Vídeo

### POST /video/generate
Gera vídeo a partir de texto e áudio.

**Request Body:**
```json
{
  "text": "Texto do vídeo",
  "audio_path": "/path/to/audio.wav",
  "template": "modern",
  "resolution": "hd"
}
```

**Response:**
```json
{
  "video_id": "uuid-456",
  "status": "processing",
  "message": "Vídeo em processamento"
}
```

### GET /video/{video_id}
Obtém status de um vídeo.

**Response:**
```json
{
  "video_id": "uuid-456",
  "status": "completed",
  "output_path": "/videos/video_123.mp4",
  "duration": 120.5
}
```

## Endpoints de TTS (Text-to-Speech)

### POST /tts/generate
Gera áudio a partir de texto.

**Request Body:**
```json
{
  "text": "Texto para converter em áudio",
  "voice": "pt-BR-Neural2-A",
  "provider": "google"
}
```

**Response:**
```json
{
  "audio_id": "uuid-789",
  "audio_path": "/audios/audio_123.wav",
  "duration": 45.2,
  "success": true
}
```

### GET /tts/status
Obtém status dos serviços TTS.

**Response:**
```json
{
  "available_providers": ["google", "azure", "aws"],
  "current_voice": "pt-BR-Neural2-A",
  "status": "operational"
}
```

## Endpoints de Avatar

### POST /avatar/generate
Gera vídeo com avatar.

**Request Body:**
```json
{
  "text": "Texto para o avatar falar",
  "avatar_style": "professional",
  "background": "office",
  "duration": 30
}
```

**Response:**
```json
{
  "avatar_id": "uuid-101",
  "status": "processing",
  "estimated_time": 120
}
```

### GET /avatar/{avatar_id}
Obtém status de um avatar.

**Response:**
```json
{
  "avatar_id": "uuid-101",
  "status": "completed",
  "video_path": "/avatars/avatar_123.mp4"
}
```

## Endpoints de Projetos

### GET /projects/
Lista projetos do usuário.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Curso de Python",
    "description": "Curso básico de Python",
    "created_at": "2024-01-15T10:30:00Z",
    "status": "active"
  }
]
```

### POST /projects/
Cria um novo projeto.

**Request Body:**
```json
{
  "name": "Novo Projeto",
  "description": "Descrição do projeto"
}
```

### GET /projects/{project_id}
Obtém detalhes de um projeto.

### PUT /projects/{project_id}
Atualiza um projeto.

### DELETE /projects/{project_id}
Remove um projeto.

## Endpoints de Dashboard

### GET /dashboard/
Obtém dados do dashboard.

**Response:**
```json
{
  "total_projects": 15,
  "total_videos": 45,
  "total_uploads": 23,
  "recent_activity": [
    {
      "type": "video_generated",
      "project": "Curso Python",
      "timestamp": "2024-01-15T14:30:00Z"
    }
  ]
}
```

## Endpoints de Sistema

### GET /health
Verifica saúde da aplicação.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "version": "2.0.0"
}
```

### GET /docs
Documentação interativa da API (Swagger UI).

### GET /redoc
Documentação alternativa da API (ReDoc).

## Códigos de Status HTTP

- `200` - Sucesso
- `201` - Criado
- `400` - Bad Request
- `401` - Não autorizado
- `403` - Proibido
- `404` - Não encontrado
- `422` - Erro de validação
- `500` - Erro interno do servidor

## Exemplos de Uso

### Exemplo completo: Upload e geração de vídeo

```bash
# 1. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password123"}'

# 2. Upload de arquivo
curl -X POST "http://localhost:8000/upload/" \
  -H "Authorization: Bearer <token>" \
  -F "file=@documento.pdf"

# 3. Gerar vídeo
curl -X POST "http://localhost:8000/video/generate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Texto do vídeo", "template": "modern"}'

# 4. Verificar status
curl -X GET "http://localhost:8000/video/<video_id>" \
  -H "Authorization: Bearer <token>"
```

## Limitações e Considerações

- Tamanho máximo de upload: 100MB
- Formatos suportados: PDF, PPTX
- Duração máxima de vídeo: 30 minutos
- Limite de requisições: 100/minuto por usuário

## Suporte

Para suporte técnico, entre em contato:
- Email: suporte@tecnocursosai.com
- Documentação: http://localhost:8000/docs 