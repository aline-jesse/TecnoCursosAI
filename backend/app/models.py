"""
Modelos de dados para TecnoCursos AI
Usando SQLAlchemy ORM com SQLite
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from .database import Base

class ProjectStatus(enum.Enum):
    """Status possíveis de um projeto"""
    DRAFT = "draft"
    PUBLISHED = "published" 
    ARCHIVED = "archived"
    UPLOADED = "uploaded"

class AssetType(enum.Enum):
    """Tipos de assets disponíveis"""
    CHARACTER = "character"      # Personagens/Avatares
    BACKGROUND = "background"    # Fundos/Cenários
    MUSIC = "music"             # Música de fundo
    SOUND_EFFECT = "sound_effect"  # Efeitos sonoros
    IMAGE = "image"             # Imagens gerais
    VIDEO = "video"             # Vídeos
    AUDIO = "audio"             # Áudios gerais
    TEXT = "text"               # Elementos de texto
    OVERLAY = "overlay"         # Sobreposições

class User(Base):
    """Modelo de usuário do sistema"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Status e permissões
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Configurações do usuário
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    language = Column(String(10), default="pt-BR")
    timezone = Column(String(50), default="America/Sao_Paulo")
    
    # Relacionamentos
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    uploads = relationship("FileUpload", back_populates="user", cascade="all, delete-orphan")
    audios = relationship("Audio", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Project(Base):
    """Modelo de projeto/curso"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    
    # Status do projeto
    status = Column(String(50), default="draft")  # draft, active, completed, archived
    is_public = Column(Boolean, default=False)
    
    # Metadados
    category = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)  # JSON string
    difficulty_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    estimated_duration = Column(Integer, nullable=True)  # em minutos
    
    # Relacionamentos
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")
    files = relationship("FileUpload", back_populates="project", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Estatísticas
    total_files = Column(Integer, default=0)
    total_videos = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Project(name='{self.name}', owner='{self.owner.username if self.owner else 'N/A'}')>"

class FileUpload(Base):
    """Modelo de arquivo carregado"""
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # em bytes
    file_type = Column(String(50), nullable=False)  # pdf, pptx, docx
    mime_type = Column(String(100), nullable=False)
    
    # Hash para verificação de integridade
    file_hash = Column(String(64), nullable=True)  # SHA256
    
    # Status do processamento
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    processing_progress = Column(Float, default=0.0)  # 0.0 a 100.0
    error_message = Column(Text, nullable=True)
    
    # Metadados extraídos
    page_count = Column(Integer, nullable=True)
    text_content = Column(Text, nullable=True)  # Conteúdo extraído do arquivo
    metadata_json = Column(Text, nullable=True)  # JSON com metadados específicos
    
    # Relacionamentos
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="uploads")
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="files")
    
    videos = relationship("Video", back_populates="source_file", cascade="all, delete-orphan")
    audios = relationship("Audio", back_populates="source_file", cascade="all, delete-orphan")
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<FileUpload(filename='{self.filename}', type='{self.file_type}', status='{self.status}')>"

class Video(Base):
    """Modelo de vídeo gerado"""
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # em bytes
    
    # Propriedades do vídeo
    duration = Column(Float, nullable=True)  # em segundos
    resolution = Column(String(20), nullable=True)  # 1920x1080, 1280x720, etc
    fps = Column(Integer, nullable=True)  # frames per second
    bitrate = Column(Integer, nullable=True)  # em kbps
    format = Column(String(10), default="mp4")
    
    # Status da geração
    status = Column(String(50), default="queued")  # queued, generating, completed, failed
    generation_progress = Column(Float, default=0.0)  # 0.0 a 100.0
    error_message = Column(Text, nullable=True)
    
    # Configurações de geração
    voice_type = Column(String(50), default="pt-br")  # Tipo de voz para narração
    background_music = Column(Boolean, default=False)
    include_captions = Column(Boolean, default=True)
    
    # Relacionamentos
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="videos")
    
    source_file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False)
    source_file = relationship("FileUpload", back_populates="videos")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Estatísticas
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Video(title='{self.title}', status='{self.status}', duration={self.duration})>"

class Audio(Base):
    """Modelo de áudio/narração gerada"""
    __tablename__ = "audios"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # em bytes
    
    # Propriedades do áudio
    duration = Column(Float, nullable=True)  # em segundos
    format = Column(String(10), default="mp3")
    bitrate = Column(String(20), nullable=True)  # 128k, 192k, etc
    sample_rate = Column(Integer, nullable=True)  # 22050, 44100, etc
    
    # Conteúdo processado
    extracted_text = Column(Text, nullable=True)  # Texto extraído do arquivo original
    text_length = Column(Integer, nullable=True)  # Tamanho do texto em caracteres
    
    # Configurações de TTS
    tts_provider = Column(String(50), default="bark")  # bark, gtts, etc
    voice_type = Column(String(50), default="v2/pt_speaker_0")  # Voz utilizada
    voice_config = Column(Text, nullable=True)  # JSON com configurações extras
    
    # Status da geração
    status = Column(String(50), default="queued")  # queued, generating, completed, failed
    generation_progress = Column(Float, default=0.0)  # 0.0 a 100.0
    error_message = Column(Text, nullable=True)
    
    # Métricas de processamento
    processing_time = Column(Float, nullable=True)  # tempo em segundos
    cache_hit = Column(Boolean, default=False)  # se foi recuperado do cache
    
    # Relacionamentos
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="audios")
    
    source_file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=True)
    source_file = relationship("FileUpload", back_populates="audios")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Estatísticas
    download_count = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Audio(title='{self.title}', status='{self.status}', duration={self.duration})>"

class Scene(Base):
    """
    Modelo de cena - representa um slide/cena do vídeo
    Cada cena contém configurações visuais e uma lista de assets
    """
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Relacionamento com projeto
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="scenes")
    
    # Informações básicas da cena
    name = Column(String(255), nullable=False, default="Nova Cena")
    ordem = Column(Integer, nullable=False, default=0)  # Ordem da cena no projeto
    texto = Column(Text, nullable=True)  # Texto principal da cena (para narração)
    duracao = Column(Float, nullable=False, default=5.0)  # Duração em segundos
    
    # Template e estilo da cena
    template_id = Column(String(100), nullable=True)  # ID do template aplicado
    template_version = Column(String(20), nullable=True)  # Versão do template
    style_preset = Column(String(50), default="default")  # modern, corporate, tech, education, minimal
    
    # Configurações visuais da cena
    background_color = Column(String(7), default="#ffffff")  # Cor de fundo (hex)
    background_type = Column(String(50), default="solid")  # solid, gradient, image, video
    background_config = Column(Text, nullable=True)  # JSON com configurações do fundo
    background_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)  # Asset de fundo
    
    # Configurações de layout e composição
    layout_type = Column(String(50), default="free")  # free, grid, columns, centered
    layout_config = Column(Text, nullable=True)  # JSON com configurações do layout
    aspect_ratio = Column(String(10), default="16:9")  # 16:9, 4:3, 1:1, 9:16
    resolution = Column(String(20), default="1920x1080")  # Resolução da cena
    
    # Configurações de transição
    transition_in = Column(String(50), default="fade")  # Transição de entrada
    transition_out = Column(String(50), default="fade")  # Transição de saída
    transition_duration = Column(Float, default=0.5)  # Duração da transição em segundos
    transition_config = Column(Text, nullable=True)  # JSON com config avançada
    
    # Configurações de áudio
    audio_track_id = Column(Integer, ForeignKey("audios.id"), nullable=True)  # Áudio principal
    background_music_id = Column(Integer, ForeignKey("assets.id"), nullable=True)  # Música de fundo
    audio_volume = Column(Float, default=1.0)  # Volume do áudio (0.0 a 1.0)
    music_volume = Column(Float, default=0.3)  # Volume da música de fundo
    
    # Configurações de animação
    animation_preset = Column(String(50), nullable=True)  # Preset de animação da cena
    animation_config = Column(Text, nullable=True)  # JSON com configurações de animação
    entrance_animation = Column(String(50), default="none")  # Animação de entrada
    exit_animation = Column(String(50), default="none")  # Animação de saída
    
    # Versionamento e colaboração
    version = Column(Integer, default=1)  # Versão da cena
    parent_scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)  # Cena pai (versioning)
    is_template = Column(Boolean, default=False)  # Se é um template
    is_public_template = Column(Boolean, default=False)  # Template público
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Criador
    last_modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Último editor
    
    # Status e metadados
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)  # Bloqueada para edição
    notes = Column(Text, nullable=True)  # Notas/observações da cena
    tags = Column(Text, nullable=True)  # Tags da cena (JSON array)
    custom_properties = Column(Text, nullable=True)  # Propriedades customizadas (JSON)
    
    # Métricas e analytics
    view_count = Column(Integer, default=0)  # Quantas vezes foi visualizada
    render_count = Column(Integer, default=0)  # Quantas vezes foi renderizada
    last_rendered = Column(DateTime(timezone=True), nullable=True)  # Último render
    render_time_avg = Column(Float, nullable=True)  # Tempo médio de render
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    assets = relationship("Asset", back_populates="scene", cascade="all, delete-orphan", order_by="Asset.camada", foreign_keys="[Asset.scene_id]", primaryjoin="Scene.id == Asset.scene_id")
    background_asset = relationship("Asset", foreign_keys=[background_asset_id], primaryjoin="Scene.background_asset_id == Asset.id")
    background_music = relationship("Asset", foreign_keys=[background_music_id], primaryjoin="Scene.background_music_id == Asset.id")
    audio_track = relationship("Audio", foreign_keys=[audio_track_id])
    creator = relationship("User", foreign_keys=[created_by])
    last_editor = relationship("User", foreign_keys=[last_modified_by])
    parent_scene = relationship("Scene", remote_side=[id])
    child_scenes = relationship("Scene", back_populates="parent_scene")
    
    def __repr__(self):
        return f"<Scene(name='{self.name}', projeto='{self.project.name if self.project else 'N/A'}', ordem={self.ordem})>"

class Asset(Base):
    """
    Modelo de asset - representa elementos visuais/sonoros em uma cena
    Pode ser personagem, imagem, música, efeito sonoro, etc.
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Relacionamento com cena (pode ser null para assets de biblioteca)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)
    scene = relationship("Scene", back_populates="assets", foreign_keys=[scene_id])
    
    # Relacionamento com projeto (para assets de biblioteca do projeto)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project")
    
    # Informações básicas do asset
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # Descrição detalhada
    tipo = Column(String(50), nullable=False)  # character, background, music, image, etc.
    subtipo = Column(String(50), nullable=True)  # Para categorização mais específica
    
    # Arquivo e recursos
    caminho_arquivo = Column(String(500), nullable=True)  # Caminho para o arquivo do asset
    url_external = Column(String(500), nullable=True)  # URL externa (se aplicável)
    file_size = Column(Integer, nullable=True)  # Tamanho do arquivo em bytes
    file_hash = Column(String(64), nullable=True)  # Hash SHA256 para verificação
    mime_type = Column(String(100), nullable=True)  # Tipo MIME do arquivo
    
    # Biblioteca de assets
    is_library_asset = Column(Boolean, default=False)  # Se é um asset de biblioteca
    is_public = Column(Boolean, default=False)  # Asset público para todos
    is_premium = Column(Boolean, default=False)  # Asset premium/pago
    library_category = Column(String(100), nullable=True)  # Categoria na biblioteca
    library_tags = Column(Text, nullable=True)  # Tags para busca (JSON array)
    license_type = Column(String(50), default="standard")  # standard, premium, royalty_free, creative_commons
    
    # Metadados do arquivo
    width = Column(Integer, nullable=True)  # Largura original (para imagens/vídeos)
    height = Column(Integer, nullable=True)  # Altura original (para imagens/vídeos)
    duration = Column(Float, nullable=True)  # Duração (para áudio/vídeo)
    format = Column(String(20), nullable=True)  # Formato do arquivo
    color_profile = Column(String(50), nullable=True)  # Perfil de cores
    metadata_json = Column(Text, nullable=True)  # Metadados específicos do tipo
    
    # Posicionamento e transformações na cena
    posicao_x = Column(Float, default=0.0)  # Posição horizontal (0.0 a 1.0 = 0% a 100%)
    posicao_y = Column(Float, default=0.0)  # Posição vertical (0.0 a 1.0 = 0% a 100%)
    escala = Column(Float, default=1.0)     # Escala do elemento (1.0 = tamanho original)
    rotacao = Column(Float, default=0.0)    # Rotação em graus
    opacidade = Column(Float, default=1.0)  # Opacidade (0.0 a 1.0)
    camada = Column(Integer, default=1)     # Camada/z-index para ordenação
    
    # Dimensões customizadas (para override das originais)
    largura = Column(Float, nullable=True)   # Largura customizada
    altura = Column(Float, nullable=True)    # Altura customizada
    
    # Configurações específicas do tipo de asset
    config_json = Column(Text, nullable=True)  # JSON com configurações específicas
    
    # Para assets de áudio/música
    volume = Column(Float, default=1.0)      # Volume do áudio (0.0 a 1.0)
    loop = Column(Boolean, default=False)    # Se o áudio deve fazer loop
    fade_in = Column(Float, default=0.0)     # Fade in em segundos
    fade_out = Column(Float, default=0.0)    # Fade out em segundos
    start_time = Column(Float, default=0.0)  # Tempo de início no áudio
    end_time = Column(Float, nullable=True)  # Tempo de fim (null = até o final)
    
    # Para assets de texto
    texto_conteudo = Column(Text, nullable=True)     # Conteúdo do texto
    fonte_familia = Column(String(100), nullable=True)  # Família da fonte
    fonte_tamanho = Column(Float, nullable=True)     # Tamanho da fonte
    fonte_cor = Column(String(7), nullable=True)     # Cor da fonte (hex)
    fonte_peso = Column(String(20), default="normal")  # normal, bold, light
    fonte_estilo = Column(String(20), default="normal")  # normal, italic
    texto_alinhamento = Column(String(20), default="center")  # left, center, right, justify
    linha_altura = Column(Float, default=1.2)        # Line height
    letra_espacamento = Column(Float, default=0.0)   # Letter spacing
    
    # Para assets de imagem/vídeo
    crop_x = Column(Float, default=0.0)      # Crop horizontal
    crop_y = Column(Float, default=0.0)      # Crop vertical
    crop_width = Column(Float, default=1.0)  # Largura do crop (ratio)
    crop_height = Column(Float, default=1.0) # Altura do crop (ratio)
    filters = Column(Text, nullable=True)    # Filtros aplicados (JSON)
    
    # Para assets de animação e efeitos
    animacao_tipo = Column(String(50), nullable=True)    # fade, slide, zoom, etc.
    animacao_duracao = Column(Float, default=0.0)        # Duração da animação
    animacao_delay = Column(Float, default=0.0)          # Delay antes da animação
    animacao_loop = Column(Boolean, default=False)       # Se animação faz loop
    animacao_config = Column(Text, nullable=True)        # JSON com configurações da animação
    easing_function = Column(String(50), default="ease")  # Função de easing
    
    # Timeline e timing
    timeline_start = Column(Float, default=0.0)  # Quando aparece na timeline (segundos)
    timeline_end = Column(Float, nullable=True)  # Quando desaparece (null = até o fim)
    timeline_locked = Column(Boolean, default=False)  # Se timing está locked
    
    # Versionamento e colaboração
    version = Column(Integer, default=1)  # Versão do asset
    parent_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)  # Asset pai
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Criador
    last_modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Último editor
    
    # Status e metadados
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)  # Se o asset está bloqueado para edição
    is_favorite = Column(Boolean, default=False)  # Se é favorito do usuário
    description = Column(Text, nullable=True)   # Descrição/notas do asset
    custom_properties = Column(Text, nullable=True)  # Propriedades customizadas (JSON)
    
    # Métricas e analytics
    usage_count = Column(Integer, default=0)  # Quantas vezes foi usado
    download_count = Column(Integer, default=0)  # Downloads (para biblioteca)
    rating_avg = Column(Float, nullable=True)  # Rating médio (0-5)
    rating_count = Column(Integer, default=0)  # Número de avaliações
    
    # Processamento e otimização
    processing_status = Column(String(50), default="ready")  # ready, processing, optimizing, failed
    processing_progress = Column(Float, default=100.0)  # Progresso do processamento
    optimized_variants = Column(Text, nullable=True)  # Variantes otimizadas (JSON)
    thumbnail_path = Column(String(500), nullable=True)  # Caminho do thumbnail
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    creator = relationship("User", foreign_keys=[created_by])
    last_editor = relationship("User", foreign_keys=[last_modified_by])
    parent_asset = relationship("Asset", remote_side=[id])
    child_assets = relationship("Asset", back_populates="parent_asset")
    
    def __repr__(self):
        return f"<Asset(name='{self.name}', tipo='{self.tipo}', cena='{self.scene.name if self.scene else 'Biblioteca'}', camada={self.camada})>"

class SceneTemplate(Base):
    """
    Modelo de template de cena - templates pré-definidos para criação rápida
    """
    __tablename__ = "scene_templates"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Informações básicas do template
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # presentation, education, marketing, etc.
    style = Column(String(50), nullable=False)  # modern, corporate, tech, education, minimal
    
    # Configurações visuais padrão
    aspect_ratio = Column(String(10), default="16:9")
    resolution = Column(String(20), default="1920x1080")
    background_type = Column(String(50), default="solid")
    background_config = Column(Text, nullable=True)  # JSON
    layout_type = Column(String(50), default="free")
    layout_config = Column(Text, nullable=True)  # JSON
    
    # Template data (JSON completo da configuração)
    template_data = Column(Text, nullable=False)  # JSON com toda estrutura do template
    
    # Assets padrão incluídos no template
    default_assets = Column(Text, nullable=True)  # JSON array com assets
    
    # Configurações
    is_public = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    tags = Column(Text, nullable=True)  # JSON array
    
    # Relacionamentos
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User")
    
    # Métricas
    usage_count = Column(Integer, default=0)
    rating_avg = Column(Float, nullable=True)
    rating_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SceneTemplate(name='{self.name}', style='{self.style}')>"

class AssetRating(Base):
    """
    Modelo de avaliação de assets
    """
    __tablename__ = "asset_ratings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Avaliação
    rating = Column(Integer, nullable=False)  # 1-5 estrelas
    comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    asset = relationship("Asset")
    user = relationship("User")
    
    def __repr__(self):
        return f"<AssetRating(asset_id={self.asset_id}, rating={self.rating})>"

class SceneComment(Base):
    """
    Modelo de comentários em cenas para colaboração
    """
    __tablename__ = "scene_comments"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Relacionamentos
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("scene_comments.id"), nullable=True)
    
    # Conteúdo
    content = Column(Text, nullable=False)
    comment_type = Column(String(50), default="general")  # general, suggestion, issue, approval
    
    # Posição no canvas (para comentários localizados)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    scene = relationship("Scene")
    user = relationship("User")
    parent_comment = relationship("SceneComment", remote_side=[id])
    replies = relationship("SceneComment", back_populates="parent_comment")
    
    def __repr__(self):
        return f"<SceneComment(scene_id={self.scene_id}, user_id={self.user_id})>"

class APIKey(Base):
    """Modelo para chaves de API"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Permissões
    scopes = Column(Text, nullable=True)  # JSON array com escopos permitidos
    is_active = Column(Boolean, default=True)
    
    # Limitações
    rate_limit = Column(Integer, default=1000)  # Requests por hora
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relacionamento
    user = relationship("User")
    
    def __repr__(self):
        return f"<APIKey(name='{self.name}', user_id={self.user_id})>" 