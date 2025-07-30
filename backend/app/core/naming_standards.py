"""
Padronização de Nomenclatura - TecnoCursos AI
Mapeamento de termos em português para inglês
"""

# Dicionário de tradução para consistência
TRANSLATION_MAP = {
    # Termos de modelo
    "usuario": "user",
    "usuarios": "users", 
    "projeto": "project",
    "projetos": "projects",
    "arquivo": "file",
    "arquivos": "files",
    "video": "video",
    "videos": "videos",
    "audio": "audio",
    "audios": "audios",
    "cena": "scene",
    "cenas": "scenes",
    "ativo": "asset",
    "ativos": "assets",
    "fundo": "background",
    "fundos": "backgrounds",
    "personagem": "character",
    "personagens": "characters",
    "efeito": "effect",
    "efeitos": "effects",
    "sobreposicao": "overlay",
    "sobreposicoes": "overlays",
    
    # Status e estados
    "rascunho": "draft",
    "publicado": "published",
    "arquivado": "archived",
    "carregado": "uploaded",
    "processando": "processing",
    "completo": "completed",
    "completado": "completed",
    "falhado": "failed",
    "erro": "error",
    "sucesso": "success",
    "pendente": "pending",
    "ativo": "active",
    "inativo": "inactive",
    "verificado": "verified",
    "nao_verificado": "unverified",
    "publico": "public",
    "privado": "private",
    
    # Campos de banco
    "nome": "name",
    "descricao": "description",
    "titulo": "title",
    "conteudo": "content",
    "criado_em": "created_at",
    "atualizado_em": "updated_at",
    "processado_em": "processed_at",
    "carregado_em": "uploaded_at",
    "completado_em": "completed_at",
    "ultimo_login": "last_login",
    "senha_hash": "hashed_password",
    "url_avatar": "avatar_url",
    "biografia": "bio",
    "idioma": "language",
    "fuso_horario": "timezone",
    "nome_completo": "full_name",
    "nome_usuario": "username",
    "email": "email",
    
    # Tipos de arquivo
    "tipo_arquivo": "file_type",
    "tipo_mime": "mime_type",
    "tamanho_arquivo": "file_size",
    "caminho_arquivo": "file_path",
    "nome_arquivo": "filename",
    "nome_original": "original_filename",
    "hash_arquivo": "file_hash",
    
    # Propriedades de mídia
    "duracao": "duration",
    "resolucao": "resolution",
    "fps": "fps",
    "bitrate": "bitrate",
    "formato": "format",
    "progresso": "progress",
    "progresso_geracao": "generation_progress",
    "progresso_processamento": "processing_progress",
    "mensagem_erro": "error_message",
    "tipo_voz": "voice_type",
    "musica_fundo": "background_music",
    "incluir_legendas": "include_captions",
    "contagem_paginas": "page_count",
    "conteudo_texto": "text_content",
    "metadados_json": "metadata_json",
    "contagem_visualizacoes": "view_count",
    "contagem_downloads": "download_count",
    "total_arquivos": "total_files",
    "total_videos": "total_videos",
    "total_visualizacoes": "total_views",
    
    # Configurações e categorias
    "categoria": "category",
    "tags": "tags",
    "nivel_dificuldade": "difficulty_level",
    "duracao_estimada": "estimated_duration",
    "iniciante": "beginner",
    "intermediario": "intermediate",
    "avancado": "advanced",
    
    # Relacionamentos
    "proprietario": "owner",
    "proprietario_id": "owner_id",
    "usuario_id": "user_id",
    "projeto_id": "project_id",
    "arquivo_origem_id": "source_file_id",
    "arquivo_origem": "source_file",
    "uploads": "uploads",
    "carregamentos": "uploads",
    
    # Tipos de asset
    "personagem": "character",
    "fundo": "background",
    "musica": "music",
    "efeito_sonoro": "sound_effect",
    "imagem": "image",
    "sobreposicao": "overlay",
    
    # Outros termos comuns
    "slug": "slug",
    "uuid": "uuid",
    "id": "id",
    "admin": "admin",
    "publico": "public",
    "eh_ativo": "is_active",
    "eh_verificado": "is_verified",
    "eh_admin": "is_admin",
    "eh_publico": "is_public"
}

# Função para padronizar nomes
def standardize_name(text: str) -> str:
    """
    Converte nomes em português para inglês usando o mapeamento
    """
    # Converter para lowercase e remover espaços
    normalized = text.lower().strip().replace(" ", "_")
    
    # Aplicar mapeamento direto se existe
    if normalized in TRANSLATION_MAP:
        return TRANSLATION_MAP[normalized]
    
    # Aplicar mapeamentos parciais
    for pt_term, en_term in TRANSLATION_MAP.items():
        if pt_term in normalized:
            normalized = normalized.replace(pt_term, en_term)
    
    return normalized

# Validação de nomenclatura
def validate_naming_consistency(file_content: str) -> list:
    """
    Valida consistência de nomenclatura em arquivo
    Retorna lista de problemas encontrados
    """
    issues = []
    lines = file_content.split('\n')
    
    # Padrões problemáticos (mistura pt/en)
    problematic_patterns = [
        ("def criar_", "should use 'create_' instead of 'criar_'"),
        ("def atualizar_", "should use 'update_' instead of 'atualizar_'"),
        ("def deletar_", "should use 'delete_' instead of 'deletar_'"),
        ("def buscar_", "should use 'search_' or 'find_' instead of 'buscar_'"),
        ("def listar_", "should use 'list_' instead of 'listar_'"),
        ("def obter_", "should use 'get_' instead of 'obter_'"),
        ("class Usuario", "should use 'User' instead of 'Usuario'"),
        ("class Projeto", "should use 'Project' instead of 'Projeto'"),
        ("class Arquivo", "should use 'File' instead of 'Arquivo'"),
        ("nome_usuario", "should use 'username' instead of 'nome_usuario'"),
        ("senha_hash", "should use 'hashed_password' instead of 'senha_hash'"),
        ("criado_em", "should use 'created_at' instead of 'criado_em'"),
        ("atualizado_em", "should use 'updated_at' instead of 'atualizado_em'"),
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern, suggestion in problematic_patterns:
            if pattern in line:
                issues.append({
                    "line": i,
                    "content": line.strip(),
                    "issue": f"Portuguese naming: {pattern}",
                    "suggestion": suggestion
                })
    
    return issues
