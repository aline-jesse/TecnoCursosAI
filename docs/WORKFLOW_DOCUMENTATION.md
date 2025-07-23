# Documentação dos Fluxos Principais - TecnoCursosAI

## Visão Geral

Esta documentação descreve os fluxos principais do sistema TecnoCursosAI, desde o upload de arquivos até a geração de vídeos com IA.

## Fluxo 1: Upload e Processamento de Arquivos

### 1.1 Upload de Arquivo
```
Usuário → Frontend → Backend → Armazenamento
```

**Detalhamento:**
1. Usuário seleciona arquivo (PDF/PPTX) no frontend
2. Frontend envia arquivo via `POST /upload/`
3. Backend valida arquivo e salva em `backend/static/uploads/`
4. Sistema retorna ID do arquivo e status

**Arquivos envolvidos:**
- `frontend/src/components/FileUpload.tsx`
- `backend/app/routers/files.py`
- `backend/services/file_processor.py`

### 1.2 Extração de Texto
```
Arquivo → Parser → Texto Extraído → Banco de Dados
```

**Detalhamento:**
1. Sistema identifica tipo de arquivo (PDF/PPTX)
2. Parser específico extrai texto e estrutura
3. Texto é limpo e processado
4. Dados são salvos no banco de dados

**Arquivos envolvidos:**
- `backend/app/parsers/pdf_parser.py`
- `backend/app/parsers/pptx_parser.py`
- `backend/app/utils.py`

## Fluxo 2: Geração de Áudio (TTS)

### 2.1 Processamento de Texto
```
Texto → Divisão em Seções → Configuração TTS → Geração
```

**Detalhamento:**
1. Texto extraído é dividido em seções menores
2. Sistema configura parâmetros TTS (voz, velocidade, etc.)
3. Cada seção é enviada para serviço TTS
4. Áudios são gerados e salvos

**Arquivos envolvidos:**
- `backend/services/tts_service.py`
- `backend/app/routers/tts.py`
- `backend/app/utils.py`

### 2.2 Integração com Provedores TTS
```
Sistema → Google TTS / Azure / AWS → Áudio Gerado
```

**Provedores suportados:**
- Google Text-to-Speech
- Microsoft Azure Speech
- Amazon Polly
- OpenAI Whisper

## Fluxo 3: Geração de Vídeos

### 3.1 Criação de Slides
```
Texto + Áudio → Template → Slides → Vídeo
```

**Detalhamento:**
1. Sistema combina texto e áudio correspondente
2. Aplica template visual (modern, corporate, tech, etc.)
3. Gera slides individuais
4. Combina slides em vídeo final

**Arquivos envolvidos:**
- `backend/app/video_engine.py`
- `backend/app/routers/video_export.py`
- `backend/app/utils.py`

### 3.2 Templates de Vídeo
```
Template → Configuração → Renderização → Vídeo Final
```

**Templates disponíveis:**
- **Modern**: Design limpo e contemporâneo
- **Corporate**: Visual profissional e formal
- **Tech**: Estilo tecnológico e futurista
- **Education**: Focado em aprendizado
- **Minimal**: Design minimalista

## Fluxo 4: Sistema de Avatares

### 4.1 Geração de Avatar
```
Texto → Avatar Style → TTS → Vídeo com Avatar
```

**Detalhamento:**
1. Usuário seleciona estilo de avatar
2. Sistema gera áudio com TTS
3. Avatar é animado com áudio
4. Vídeo final é renderizado

**Arquivos envolvidos:**
- `backend/services/avatar_video_generator.py`
- `backend/app/routers/avatar.py`
- `backend/app/avatar_utils.py`

### 4.2 Estilos de Avatar
```
Estilo → Configuração → Renderização → Avatar Final
```

**Estilos disponíveis:**
- **Professional**: Avatar formal e profissional
- **Friendly**: Avatar amigável e acessível
- **Teacher**: Avatar educacional
- **Minimalist**: Avatar simples e clean

## Fluxo 5: Sistema de Autenticação

### 5.1 Registro de Usuário
```
Dados → Validação → Hash Senha → Banco → Token
```

**Detalhamento:**
1. Usuário fornece dados de registro
2. Sistema valida informações
3. Senha é hasheada com bcrypt
4. Usuário é criado no banco
5. Token JWT é gerado

**Arquivos envolvidos:**
- `backend/app/auth.py`
- `backend/app/routers/auth.py`
- `backend/app/models.py`

### 5.2 Login e Autenticação
```
Credenciais → Validação → Token JWT → Sessão
```

**Detalhamento:**
1. Usuário fornece credenciais
2. Sistema valida senha
3. Token JWT é gerado
4. Token é usado para autenticação

## Fluxo 6: Sistema de Projetos

### 6.1 Criação de Projeto
```
Dados → Validação → Banco → Estrutura → Projeto
```

**Detalhamento:**
1. Usuário cria novo projeto
2. Sistema valida dados
3. Projeto é salvo no banco
4. Estrutura de pastas é criada
5. Projeto fica disponível para uso

**Arquivos envolvidos:**
- `backend/app/routers/projects.py`
- `backend/app/models.py`
- `backend/app/schemas.py`

### 6.2 Gerenciamento de Projetos
```
Projeto → Arquivos → Processamento → Resultados
```

**Funcionalidades:**
- Upload de múltiplos arquivos
- Processamento em lote
- Histórico de atividades
- Compartilhamento de projetos

## Fluxo 7: Sistema de Notificações

### 7.1 Notificações em Tempo Real
```
Evento → WebSocket → Frontend → Notificação
```

**Detalhamento:**
1. Evento ocorre no backend
2. Sistema envia notificação via WebSocket
3. Frontend recebe e exibe notificação
4. Usuário é informado em tempo real

**Arquivos envolvidos:**
- `backend/app/websocket_notifications.py`
- `backend/services/notification_service.py`
- `frontend/src/hooks/useWebSocket.ts`

### 7.2 Tipos de Notificação
```
Tipo → Configuração → Canal → Usuário
```

**Tipos disponíveis:**
- **Upload**: Confirmação de upload
- **Processing**: Status de processamento
- **Complete**: Conclusão de tarefa
- **Error**: Erro no processamento

## Fluxo 8: Sistema de Cache

### 8.1 Cache de Processamento
```
Dados → Cache → Verificação → Retorno
```

**Detalhamento:**
1. Sistema verifica cache antes de processar
2. Se dados existem, retorna do cache
3. Se não existem, processa e salva no cache
4. Performance é otimizada

**Arquivos envolvidos:**
- `backend/services/cache_service.py`
- `backend/app/middleware/cache_middleware.py`

### 8.2 Estratégias de Cache
```
Estratégia → Configuração → Aplicação → Resultado
```

**Estratégias:**
- **LRU**: Least Recently Used
- **TTL**: Time To Live
- **Write-Through**: Escrita imediata
- **Write-Back**: Escrita diferida

## Fluxo 9: Sistema de Monitoramento

### 9.1 Coleta de Métricas
```
Sistema → Métricas → Armazenamento → Dashboard
```

**Detalhamento:**
1. Sistema coleta métricas em tempo real
2. Dados são armazenados
3. Dashboard exibe informações
4. Alertas são gerados quando necessário

**Arquivos envolvidos:**
- `backend/app/monitoring.py`
- `backend/app/routers/analytics.py`
- `backend/services/performance_monitor.py`

### 9.2 Métricas Coletadas
```
Métrica → Coleta → Processamento → Visualização
```

**Métricas principais:**
- Performance de processamento
- Uso de recursos
- Erros e exceções
- Atividade de usuários

## Fluxo 10: Sistema de Backup

### 10.1 Backup Automático
```
Agendamento → Coleta → Compressão → Armazenamento
```

**Detalhamento:**
1. Sistema agenda backups automáticos
2. Coleta dados do banco e arquivos
3. Comprime dados
4. Salva em local seguro

**Arquivos envolvidos:**
- `scripts/auto_backup.py`
- `backend/services/backup_service.py`
- `scripts/backup_and_restore.py`

### 10.2 Restauração
```
Backup → Validação → Restauração → Verificação
```

**Detalhamento:**
1. Sistema seleciona backup
2. Valida integridade dos dados
3. Restaura dados
4. Verifica funcionamento

## Diagramas de Fluxo

### Fluxo Completo: Upload → Vídeo
```
[Upload] → [Extração] → [TTS] → [Slides] → [Vídeo] → [Download]
```

### Fluxo de Autenticação
```
[Login] → [Validação] → [Token] → [Acesso] → [Logout]
```

### Fluxo de Avatar
```
[Texto] → [TTS] → [Avatar] → [Animação] → [Vídeo]
```

## Considerações de Performance

### Otimizações Implementadas
- Cache inteligente para evitar reprocessamento
- Processamento assíncrono para tarefas longas
- Compressão de arquivos para economia de espaço
- Load balancing para distribuição de carga

### Limitações Conhecidas
- Tamanho máximo de upload: 100MB
- Duração máxima de vídeo: 30 minutos
- Limite de concorrência: 10 usuários simultâneos
- Tempo de processamento: 2-5 minutos por vídeo

## Troubleshooting

### Problemas Comuns e Soluções

1. **Upload falha**
   - Verificar tamanho do arquivo
   - Validar formato suportado
   - Verificar espaço em disco

2. **TTS não funciona**
   - Verificar conectividade com provedor
   - Validar configurações de API
   - Verificar quota de uso

3. **Vídeo não gera**
   - Verificar dependências (FFmpeg)
   - Validar templates disponíveis
   - Verificar espaço em disco

4. **Avatar não funciona**
   - Verificar configurações de avatar
   - Validar integração com TTS
   - Verificar recursos de sistema

## Próximos Passos

### Melhorias Planejadas
- Suporte a mais formatos de entrada
- Templates de vídeo personalizáveis
- Sistema de plugins para extensibilidade
- Integração com mais provedores TTS
- Dashboard avançado de analytics 