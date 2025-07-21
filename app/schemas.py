"""
Schemas Pydantic para validação de dados da API TecnoCursos AI
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Union, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
import re

# ========================= BASE SCHEMAS =========================

class BaseResponse(BaseModel):
    """Schema base para respostas da API"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ========================= USER SCHEMAS =========================

class UserBase(BaseModel):
    """Schema base para usuário"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    language: str = Field(default="pt-BR", max_length=10)
    timezone: str = Field(default="America/Sao_Paulo", max_length=50)

class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username deve conter apenas letras, números e underscore')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve ter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve ter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Senha deve ter pelo menos um número')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Senhas não coincidem')
        return v

class UserLogin(BaseModel):
    """Schema para login de usuário"""
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)

class UserResponse(BaseModel):
    """Schema de resposta para usuário"""
    id: int
    uuid: str
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    language: str
    timezone: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserProfile(UserResponse):
    """Schema detalhado do perfil do usuário"""
    updated_at: Optional[datetime]
    total_projects: int = 0
    total_uploads: int = 0
    
    class Config:
        from_attributes = True

# ========================= PROJECT SCHEMAS =========================

class ProjectBase(BaseModel):
    """Schema base para projeto"""
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=1000)
    difficulty_level: str = Field(default="beginner", max_length=20)
    estimated_duration: Optional[int] = Field(None, gt=0)
    is_public: bool = Field(default=False)
    
    @validator('difficulty_level')
    def validate_difficulty(cls, v):
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if v not in valid_levels:
            raise ValueError(f'Nível deve ser um de: {", ".join(valid_levels)}')
        return v

class ProjectCreate(ProjectBase):
    """Schema para criação de projeto"""
    pass

class ProjectUpdate(BaseModel):
    """Schema para atualização de projeto"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=1000)
    difficulty_level: Optional[str] = Field(None, max_length=20)
    estimated_duration: Optional[int] = Field(None, gt=0)
    is_public: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50)

class ProjectResponse(BaseModel):
    """Schema de resposta para projeto"""
    id: int
    uuid: str
    name: str
    description: Optional[str]
    slug: str
    status: str
    is_public: bool
    category: Optional[str]
    tags: Optional[str]
    difficulty_level: str
    estimated_duration: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    total_files: int
    total_videos: int
    total_views: int
    owner_id: int
    
    class Config:
        from_attributes = True

class ProjectDetail(ProjectResponse):
    """Schema detalhado do projeto com relacionamentos"""
    owner: UserResponse
    
    class Config:
        from_attributes = True

class ProjectSummary(BaseModel):
    """Schema resumido para listagem de projetos"""
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    files_count: int = Field(default=0, description="Número de arquivos no projeto")
    videos_count: int = Field(default=0, description="Número de vídeos no projeto")
    
    class Config:
        from_attributes = True

# ========================= FILE UPLOAD SCHEMAS =========================

class FileUploadBase(BaseModel):
    """Schema base para upload de arquivo"""
    filename: str = Field(..., max_length=255)
    original_filename: str = Field(..., max_length=255)
    file_type: str = Field(..., max_length=50)
    file_size: int = Field(..., gt=0)

class FileUploadCreate(FileUploadBase):
    """Schema para criação de upload de arquivo"""
    project_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=500)

class FileUploadResponse(BaseModel):
    """Schema de resposta para upload de arquivo"""
    id: int
    uuid: str
    filename: str
    file_size: int
    file_type: str
    status: str
    created_at: datetime
    project_id: int
    has_thumbnail: bool = False

    class Config:
        from_attributes = True

class FileListResponse(BaseModel):
    """Schema de resposta para listagem de arquivos"""
    files: List[FileUploadResponse]
    total: int
    skip: int
    limit: int

class FileStatsResponse(BaseModel):
    """Schema de resposta para estatísticas de arquivos"""
    total_files: int
    total_size: int
    file_types: dict
    status_counts: dict

class FileProcessingStatus(BaseModel):
    """Schema para status de processamento"""
    file_id: int
    filename: str
    status: str
    progress: float
    error_message: Optional[str] = None
    estimated_time_remaining: Optional[int] = None

# ========================= VIDEO SCHEMAS =========================

class VideoBase(BaseModel):
    """Schema base para vídeo"""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    voice_type: str = Field(default="pt-br", max_length=50)
    background_music: bool = Field(default=False)
    include_captions: bool = Field(default=True)

class VideoCreate(VideoBase):
    """Schema para criação de vídeo"""
    source_file_id: int

class VideoResponse(BaseModel):
    """Schema de resposta para vídeo"""
    id: int
    uuid: str
    title: str
    description: Optional[str]
    filename: str
    file_path: str
    file_size: Optional[int]
    duration: Optional[float]
    resolution: Optional[str]
    fps: Optional[int]
    format: str
    status: str
    generation_progress: float
    voice_type: str
    background_music: bool
    include_captions: bool
    created_at: datetime
    completed_at: Optional[datetime]
    view_count: int
    download_count: int
    project_id: int
    source_file_id: int
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

# ========================= AUTHENTICATION SCHEMAS =========================

class Token(BaseModel):
    """Schema para resposta de token"""
    access_token: str
    token_type: str
    expires_in: int = 1800  # 30 minutos em segundos
    refresh_token: str

class TokenRefresh(BaseModel):
    """Schema para refresh de token"""
    refresh_token: str

class TokenData(BaseModel):
    """Schema para dados do token"""
    email: Optional[str] = None
    user_id: Optional[int] = None

class PasswordChange(BaseModel):
    """Schema para mudança de senha"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Nova senha deve ter pelo menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Nova senha deve ter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Nova senha deve ter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Nova senha deve ter pelo menos um número')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Senhas não coincidem')
        return v

# ========================= API RESPONSE SCHEMAS =========================

class SuccessResponse(BaseResponse):
    """Schema para resposta de sucesso"""
    data: Optional[dict] = None

class ErrorResponse(BaseResponse):
    """Schema para resposta de erro"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[dict] = None

class PaginatedResponse(BaseModel):
    """Schema para respostas paginadas"""
    items: List[dict]
    total: int
    page: int = Field(..., gt=0)
    size: int = Field(..., gt=0, le=100)
    pages: int
    has_next: bool
    has_prev: bool

class FileUploadRequest(BaseModel):
    """Schema para request de upload"""
    project_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=1000)

# ========================= STATISTICS SCHEMAS =========================

class UserStats(BaseModel):
    """Schema para estatísticas do usuário"""
    total_projects: int = 0
    total_uploads: int = 0
    total_videos: int = 0
    storage_used: int = 0  # em bytes
    last_activity: Optional[datetime] = None

class ProjectStats(BaseModel):
    """Schema para estatísticas do projeto"""
    total_files: int = 0
    total_videos: int = 0
    total_views: int = 0
    total_downloads: int = 0
    average_rating: Optional[float] = None

class SystemStats(BaseModel):
    """Schema para estatísticas do sistema"""
    total_users: int = 0
    total_projects: int = 0
    total_files: int = 0
    total_videos: int = 0
    storage_used: int = 0  # em bytes
    active_users_today: int = 0
    uploads_today: int = 0
    videos_generated_today: int = 0

class HealthCheck(BaseModel):
    """Schema para health check do sistema"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "2.0.0"
    uptime_seconds: Optional[float] = None
    database_status: str = "connected"
    services_status: Dict[str, str] = Field(default_factory=dict)

# ========================= AUDIO SCHEMAS =========================

class AudioCreate(BaseModel):
    """Schema para criação de áudio"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    filename: str = Field(..., max_length=255)
    file_path: str = Field(..., max_length=500)
    file_size: Optional[int] = None
    duration: Optional[float] = None
    format: Optional[str] = Field(default="mp3", max_length=10)
    extracted_text: Optional[str] = None
    text_length: Optional[int] = None
    tts_provider: Optional[str] = Field(default="gtts", max_length=50)
    voice_type: Optional[str] = Field(default="pt-br", max_length=50)
    voice_config: Optional[str] = None
    
class AudioResponse(BaseModel):
    """Schema de resposta para áudio"""
    id: int
    uuid: str
    title: str
    description: Optional[str]
    filename: str
    file_path: str
    file_size: Optional[int]
    duration: Optional[float]
    format: Optional[str]
    bitrate: Optional[str]
    sample_rate: Optional[int]
    extracted_text: Optional[str]
    text_length: Optional[int]
    tts_provider: Optional[str]
    voice_type: Optional[str]
    voice_config: Optional[str]
    status: Optional[str]
    generation_progress: Optional[float]
    error_message: Optional[str]
    processing_time: Optional[float]
    cache_hit: Optional[bool]
    user_id: int
    source_file_id: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    download_count: int = 0
    play_count: int = 0
    
    class Config:
        from_attributes = True

# ========================= SCENE SCHEMAS =========================

class SceneBase(BaseModel):
    """Schema base para cena"""
    name: str = Field(..., min_length=1, max_length=255)
    ordem: int = Field(..., ge=0)
    texto: Optional[str] = None
    duracao: float = Field(5.0, gt=0)
    
    # Template e estilo
    template_id: Optional[str] = Field(None, max_length=100)
    template_version: Optional[str] = Field(None, max_length=20)
    style_preset: str = Field("default", max_length=50)
    
    # Configurações visuais
    background_color: str = Field("#ffffff", pattern="^#[0-9a-fA-F]{6}$")
    background_type: str = Field("solid", pattern="^(solid|gradient|image|video)$")
    background_config: Optional[str] = None
    background_asset_id: Optional[int] = None
    
    # Layout e composição
    layout_type: str = Field("free", pattern="^(free|grid|columns|centered)$")
    layout_config: Optional[str] = None
    aspect_ratio: str = Field("16:9", pattern="^(16:9|4:3|1:1|9:16)$")
    resolution: str = Field("1920x1080", pattern="^\\d+x\\d+$")
    
    # Transições
    transition_in: str = Field("fade", max_length=50)
    transition_out: str = Field("fade", max_length=50)
    transition_duration: float = Field(0.5, ge=0)
    transition_config: Optional[str] = None
    
    # Áudio
    audio_track_id: Optional[int] = None
    background_music_id: Optional[int] = None
    audio_volume: float = Field(1.0, ge=0, le=1)
    music_volume: float = Field(0.3, ge=0, le=1)
    
    # Animação
    animation_preset: Optional[str] = Field(None, max_length=50)
    animation_config: Optional[str] = None
    entrance_animation: str = Field("none", max_length=50)
    exit_animation: str = Field("none", max_length=50)
    
    # Versionamento
    version: int = Field(1, ge=1)
    parent_scene_id: Optional[int] = None
    is_template: bool = False
    is_public_template: bool = False
    
    # Status e metadados
    is_active: bool = True
    is_locked: bool = False
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_properties: Optional[Dict[str, Any]] = None

class SceneCreate(SceneBase):
    """Schema para criação de cena"""
    project_id: int

class SceneUpdate(BaseModel):
    """Schema para atualização de cena"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    ordem: Optional[int] = Field(None, ge=0)
    texto: Optional[str] = None
    duracao: Optional[float] = Field(None, gt=0)
    
    # Template e estilo
    template_id: Optional[str] = Field(None, max_length=100)
    template_version: Optional[str] = Field(None, max_length=20)
    style_preset: Optional[str] = Field(None, max_length=50)
    
    # Configurações visuais
    background_color: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    background_type: Optional[str] = Field(None, pattern="^(solid|gradient|image|video)$")
    background_config: Optional[str] = None
    background_asset_id: Optional[int] = None
    
    # Layout e composição
    layout_type: Optional[str] = Field(None, pattern="^(free|grid|columns|centered)$")
    layout_config: Optional[str] = None
    aspect_ratio: Optional[str] = Field(None, pattern="^(16:9|4:3|1:1|9:16)$")
    resolution: Optional[str] = Field(None, pattern="^\\d+x\\d+$")
    
    # Transições
    transition_in: Optional[str] = Field(None, max_length=50)
    transition_out: Optional[str] = Field(None, max_length=50)
    transition_duration: Optional[float] = Field(None, ge=0)
    transition_config: Optional[str] = None
    
    # Áudio
    audio_track_id: Optional[int] = None
    background_music_id: Optional[int] = None
    audio_volume: Optional[float] = Field(None, ge=0, le=1)
    music_volume: Optional[float] = Field(None, ge=0, le=1)
    
    # Animação
    animation_preset: Optional[str] = Field(None, max_length=50)
    animation_config: Optional[str] = None
    entrance_animation: Optional[str] = Field(None, max_length=50)
    exit_animation: Optional[str] = Field(None, max_length=50)
    
    # Versionamento
    version: Optional[int] = Field(None, ge=1)
    parent_scene_id: Optional[int] = None
    is_template: Optional[bool] = None
    is_public_template: Optional[bool] = None
    
    # Status e metadados
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_properties: Optional[Dict[str, Any]] = None

class SceneResponse(SceneBase):
    """Schema de resposta para cena"""
    id: int
    uuid: str
    project_id: int
    created_by: Optional[int]
    last_modified_by: Optional[int]
    
    # Métricas
    view_count: int = 0
    render_count: int = 0
    last_rendered: Optional[datetime] = None
    render_time_avg: Optional[float] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========================= ASSET SCHEMAS =========================

class AssetBase(BaseModel):
    """Schema base para asset"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tipo: str = Field(..., max_length=50)  # character, background, music, image, etc.
    subtipo: Optional[str] = Field(None, max_length=50)
    
    # Arquivo e recursos
    caminho_arquivo: Optional[str] = Field(None, max_length=500)
    url_external: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # Biblioteca de assets
    is_library_asset: bool = False
    is_public: bool = False
    is_premium: bool = False
    library_category: Optional[str] = Field(None, max_length=100)
    library_tags: Optional[List[str]] = None
    license_type: str = Field("standard", pattern="^(standard|premium|royalty_free|creative_commons)$")
    
    # Metadados do arquivo
    width: Optional[int] = Field(None, ge=0)
    height: Optional[int] = Field(None, ge=0)
    duration: Optional[float] = Field(None, ge=0)
    format: Optional[str] = Field(None, max_length=20)
    color_profile: Optional[str] = Field(None, max_length=50)
    
    # Posicionamento e transformações na cena
    posicao_x: float = Field(0.0, ge=0, le=1)
    posicao_y: float = Field(0.0, ge=0, le=1)
    escala: float = Field(1.0, gt=0)
    rotacao: float = Field(0.0, ge=-360, le=360)
    opacidade: float = Field(1.0, ge=0, le=1)
    camada: int = Field(1, ge=0)
    
    # Dimensões customizadas
    largura: Optional[float] = Field(None, gt=0)
    altura: Optional[float] = Field(None, gt=0)
    
    # Para assets de áudio/música
    volume: float = Field(1.0, ge=0, le=1)
    loop: bool = False
    fade_in: float = Field(0.0, ge=0)
    fade_out: float = Field(0.0, ge=0)
    start_time: float = Field(0.0, ge=0)
    end_time: Optional[float] = Field(None, gt=0)
    
    # Para assets de texto
    texto_conteudo: Optional[str] = None
    fonte_familia: Optional[str] = Field(None, max_length=100)
    fonte_tamanho: Optional[float] = Field(None, gt=0)
    fonte_cor: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    fonte_peso: str = Field("normal", pattern="^(normal|bold|light)$")
    fonte_estilo: str = Field("normal", pattern="^(normal|italic)$")
    texto_alinhamento: str = Field("center", pattern="^(left|center|right|justify)$")
    linha_altura: float = Field(1.2, gt=0)
    letra_espacamento: float = 0.0
    
    # Para assets de imagem/vídeo
    crop_x: float = Field(0.0, ge=0, le=1)
    crop_y: float = Field(0.0, ge=0, le=1)
    crop_width: float = Field(1.0, gt=0, le=1)
    crop_height: float = Field(1.0, gt=0, le=1)
    filters: Optional[Dict[str, Any]] = None
    
    # Para assets de animação e efeitos
    animacao_tipo: Optional[str] = Field(None, max_length=50)
    animacao_duracao: float = Field(0.0, ge=0)
    animacao_delay: float = Field(0.0, ge=0)
    animacao_loop: bool = False
    animacao_config: Optional[Dict[str, Any]] = None
    easing_function: str = Field("ease", max_length=50)
    
    # Timeline e timing
    timeline_start: float = Field(0.0, ge=0)
    timeline_end: Optional[float] = Field(None, gt=0)
    timeline_locked: bool = False
    
    # Versionamento e colaboração
    version: int = Field(1, ge=1)
    parent_asset_id: Optional[int] = None
    
    # Status e metadados
    is_active: bool = True
    is_locked: bool = False
    is_favorite: bool = False
    custom_properties: Optional[Dict[str, Any]] = None
    
    # Processamento
    processing_status: str = Field("ready", pattern="^(ready|processing|optimizing|failed)$")

class AssetCreate(AssetBase):
    """Schema para criação de asset"""
    scene_id: Optional[int] = None  # Pode ser null para assets de biblioteca
    project_id: Optional[int] = None  # Para assets de biblioteca do projeto

class AssetUpdate(BaseModel):
    """Schema para atualização de asset"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tipo: Optional[str] = Field(None, max_length=50)
    subtipo: Optional[str] = Field(None, max_length=50)
    
    # Arquivo e recursos
    caminho_arquivo: Optional[str] = Field(None, max_length=500)
    url_external: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # Biblioteca de assets
    is_library_asset: Optional[bool] = None
    is_public: Optional[bool] = None
    is_premium: Optional[bool] = None
    library_category: Optional[str] = Field(None, max_length=100)
    library_tags: Optional[List[str]] = None
    license_type: Optional[str] = Field(None, pattern="^(standard|premium|royalty_free|creative_commons)$")
    
    # Metadados do arquivo
    width: Optional[int] = Field(None, ge=0)
    height: Optional[int] = Field(None, ge=0)
    duration: Optional[float] = Field(None, ge=0)
    format: Optional[str] = Field(None, max_length=20)
    color_profile: Optional[str] = Field(None, max_length=50)
    
    # Posicionamento e transformações na cena
    posicao_x: Optional[float] = Field(None, ge=0, le=1)
    posicao_y: Optional[float] = Field(None, ge=0, le=1)
    escala: Optional[float] = Field(None, gt=0)
    rotacao: Optional[float] = Field(None, ge=-360, le=360)
    opacidade: Optional[float] = Field(None, ge=0, le=1)
    camada: Optional[int] = Field(None, ge=0)
    
    # Dimensões customizadas
    largura: Optional[float] = Field(None, gt=0)
    altura: Optional[float] = Field(None, gt=0)
    
    # Para assets de áudio/música
    volume: Optional[float] = Field(None, ge=0, le=1)
    loop: Optional[bool] = None
    fade_in: Optional[float] = Field(None, ge=0)
    fade_out: Optional[float] = Field(None, ge=0)
    start_time: Optional[float] = Field(None, ge=0)
    end_time: Optional[float] = Field(None, gt=0)
    
    # Para assets de texto
    texto_conteudo: Optional[str] = None
    fonte_familia: Optional[str] = Field(None, max_length=100)
    fonte_tamanho: Optional[float] = Field(None, gt=0)
    fonte_cor: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    fonte_peso: Optional[str] = Field(None, pattern="^(normal|bold|light)$")
    fonte_estilo: Optional[str] = Field(None, pattern="^(normal|italic)$")
    texto_alinhamento: Optional[str] = Field(None, pattern="^(left|center|right|justify)$")
    linha_altura: Optional[float] = Field(None, gt=0)
    letra_espacamento: Optional[float] = None
    
    # Para assets de imagem/vídeo
    crop_x: Optional[float] = Field(None, ge=0, le=1)
    crop_y: Optional[float] = Field(None, ge=0, le=1)
    crop_width: Optional[float] = Field(None, gt=0, le=1)
    crop_height: Optional[float] = Field(None, gt=0, le=1)
    filters: Optional[Dict[str, Any]] = None
    
    # Para assets de animação e efeitos
    animacao_tipo: Optional[str] = Field(None, max_length=50)
    animacao_duracao: Optional[float] = Field(None, ge=0)
    animacao_delay: Optional[float] = Field(None, ge=0)
    animacao_loop: Optional[bool] = None
    animacao_config: Optional[Dict[str, Any]] = None
    easing_function: Optional[str] = Field(None, max_length=50)
    
    # Timeline e timing
    timeline_start: Optional[float] = Field(None, ge=0)
    timeline_end: Optional[float] = Field(None, gt=0)
    timeline_locked: Optional[bool] = None
    
    # Versionamento
    version: Optional[int] = Field(None, ge=1)
    parent_asset_id: Optional[int] = None
    
    # Status e metadados
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    is_favorite: Optional[bool] = None
    custom_properties: Optional[Dict[str, Any]] = None
    
    # Processamento
    processing_status: Optional[str] = Field(None, pattern="^(ready|processing|optimizing|failed)$")

class AssetResponse(AssetBase):
    """Schema de resposta para asset"""
    id: int
    uuid: str
    scene_id: Optional[int]
    project_id: Optional[int]
    file_hash: Optional[str]
    created_by: Optional[int]
    last_modified_by: Optional[int]
    
    # Métricas
    usage_count: int = 0
    download_count: int = 0
    rating_avg: Optional[float] = None
    rating_count: int = 0
    
    # Processamento
    processing_progress: float = 100.0
    optimized_variants: Optional[Dict[str, Any]] = None
    thumbnail_path: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========================= SCENE TEMPLATE SCHEMAS =========================

class SceneTemplateBase(BaseModel):
    """Schema base para template de cena"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    style: str = Field(..., pattern="^(modern|corporate|tech|education|minimal)$")
    aspect_ratio: str = Field("16:9", pattern="^(16:9|4:3|1:1|9:16)$")
    resolution: str = Field("1920x1080", pattern="^\\d+x\\d+$")
    background_type: str = Field("solid", pattern="^(solid|gradient|image|video)$")
    background_config: Optional[Dict[str, Any]] = None
    layout_type: str = Field("free", pattern="^(free|grid|columns|centered)$")
    layout_config: Optional[Dict[str, Any]] = None
    template_data: Dict[str, Any] = Field(..., description="JSON com toda estrutura do template")
    default_assets: Optional[List[Dict[str, Any]]] = None
    is_public: bool = False
    is_premium: bool = False
    is_featured: bool = False
    tags: Optional[List[str]] = None

class SceneTemplateCreate(SceneTemplateBase):
    """Schema para criação de template de cena"""
    pass

class SceneTemplateUpdate(BaseModel):
    """Schema para atualização de template de cena"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    style: Optional[str] = Field(None, pattern="^(modern|corporate|tech|education|minimal)$")
    aspect_ratio: Optional[str] = Field(None, pattern="^(16:9|4:3|1:1|9:16)$")
    resolution: Optional[str] = Field(None, pattern="^\\d+x\\d+$")
    background_type: Optional[str] = Field(None, pattern="^(solid|gradient|image|video)$")
    background_config: Optional[Dict[str, Any]] = None
    layout_type: Optional[str] = Field(None, pattern="^(free|grid|columns|centered)$")
    layout_config: Optional[Dict[str, Any]] = None
    template_data: Optional[Dict[str, Any]] = None
    default_assets: Optional[List[Dict[str, Any]]] = None
    is_public: Optional[bool] = None
    is_premium: Optional[bool] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None

class SceneTemplateResponse(SceneTemplateBase):
    """Schema de resposta para template de cena"""
    id: int
    uuid: str
    created_by: int
    usage_count: int = 0
    rating_avg: Optional[float] = None
    rating_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========================= ASSET RATING SCHEMAS =========================

class AssetRatingBase(BaseModel):
    """Schema base para avaliação de asset"""
    rating: int = Field(..., ge=1, le=5, description="Avaliação de 1 a 5 estrelas")
    comment: Optional[str] = Field(None, max_length=1000)

class AssetRatingCreate(AssetRatingBase):
    """Schema para criação de avaliação"""
    asset_id: int

class AssetRatingUpdate(BaseModel):
    """Schema para atualização de avaliação"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)

class AssetRatingResponse(AssetRatingBase):
    """Schema de resposta para avaliação"""
    id: int
    asset_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========================= SCENE COMMENT SCHEMAS =========================

class SceneCommentBase(BaseModel):
    """Schema base para comentário de cena"""
    content: str = Field(..., min_length=1, max_length=2000)
    comment_type: str = Field("general", pattern="^(general|suggestion|issue|approval)$")
    position_x: Optional[float] = Field(None, ge=0, le=1)
    position_y: Optional[float] = Field(None, ge=0, le=1)
    is_important: bool = False

class SceneCommentCreate(SceneCommentBase):
    """Schema para criação de comentário"""
    scene_id: int
    parent_comment_id: Optional[int] = None

class SceneCommentUpdate(BaseModel):
    """Schema para atualização de comentário"""
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    comment_type: Optional[str] = Field(None, pattern="^(general|suggestion|issue|approval)$")
    position_x: Optional[float] = Field(None, ge=0, le=1)
    position_y: Optional[float] = Field(None, ge=0, le=1)
    is_resolved: Optional[bool] = None
    is_important: Optional[bool] = None

class SceneCommentResponse(SceneCommentBase):
    """Schema de resposta para comentário"""
    id: int
    uuid: str
    scene_id: int
    user_id: int
    parent_comment_id: Optional[int] = None
    is_resolved: bool = False
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Lista de respostas (para comentários aninhados)
    replies: List['SceneCommentResponse'] = []
    
    class Config:
        from_attributes = True

# Permitir referências circulares para comentários aninhados
SceneCommentResponse.model_rebuild() 

# ========================= PAGINATION SCHEMAS =========================

class PaginationMeta(BaseModel):
    """Metadados de paginação"""
    page: int = Field(..., ge=1, description="Página atual")
    size: int = Field(..., ge=1, le=100, description="Itens por página")
    total: int = Field(..., ge=0, description="Total de itens")
    pages: int = Field(..., ge=0, description="Total de páginas")
    has_next: bool = Field(..., description="Tem próxima página")
    has_prev: bool = Field(..., description="Tem página anterior")
    next_page: Optional[int] = Field(None, description="Número da próxima página")
    prev_page: Optional[int] = Field(None, description="Número da página anterior")

class PaginatedSceneResponse(BaseModel):
    """Resposta paginada para cenas"""
    items: List[SceneResponse] = Field(..., description="Lista de cenas")
    meta: PaginationMeta = Field(..., description="Metadados de paginação")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Filtros aplicados")
    
class SceneSummary(BaseModel):
    """Resumo de cena para listagens otimizadas"""
    id: int
    uuid: str
    name: str
    ordem: int
    duracao: float
    style_preset: str
    background_color: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    project_id: int
    assets_count: int = Field(default=0, description="Número de assets na cena")
    
    class Config:
        from_attributes = True

class SceneDetailResponse(SceneResponse):
    """Resposta detalhada de cena com assets incluídos"""
    assets: List[Dict[str, Any]] = Field(default_factory=list, description="Assets da cena")
    comments_count: int = Field(default=0, description="Número de comentários")
    view_count: int = Field(default=0, description="Número de visualizações")
    
    class Config:
        from_attributes = True

class SceneCreateResponse(BaseModel):
    """Resposta específica para criação de cena"""
    id: int
    uuid: str
    name: str
    project_id: int
    message: str = "Cena criada com sucesso"
    created_at: datetime
    
    class Config:
        from_attributes = True

class SceneUpdateResponse(BaseModel):
    """Resposta específica para atualização de cena"""
    id: int
    uuid: str
    name: str
    message: str = "Cena atualizada com sucesso"
    updated_at: datetime
    changes_applied: List[str] = Field(default_factory=list, description="Campos alterados")
    
    class Config:
        from_attributes = True

class SceneDeleteResponse(BaseModel):
    """Resposta para deleção de cena"""
    id: int
    name: str
    message: str = "Cena deletada com sucesso"
    deleted_at: datetime = Field(default_factory=datetime.utcnow)

# ========================= ADVANCED FILTERING SCHEMAS =========================

class SceneFilterParams(BaseModel):
    """Parâmetros avançados de filtro para cenas"""
    project_id: Optional[int] = Field(None, description="ID do projeto")
    template_id: Optional[str] = Field(None, description="ID do template")
    style_preset: Optional[str] = Field(None, description="Estilo da cena")
    is_template: Optional[bool] = Field(None, description="Filtrar templates")
    is_active: Optional[bool] = Field(None, description="Filtrar por status ativo")
    search: Optional[str] = Field(None, min_length=3, description="Busca por nome ou texto")
    duration_min: Optional[float] = Field(None, ge=0, description="Duração mínima")
    duration_max: Optional[float] = Field(None, gt=0, description="Duração máxima")
    created_after: Optional[datetime] = Field(None, description="Criadas após data")
    created_before: Optional[datetime] = Field(None, description="Criadas antes da data")
    order_by: str = Field("ordem", description="Campo para ordenação")
    order_direction: str = Field("asc", pattern="^(asc|desc)$", description="Direção da ordenação")

class BulkSceneOperation(BaseModel):
    """Operação em lote para cenas"""
    scene_ids: List[int] = Field(..., min_items=1, max_items=50, description="IDs das cenas")
    operation: str = Field(..., pattern="^(delete|duplicate|reorder|update_style)$")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros da operação")

class BulkOperationResponse(BaseModel):
    """Resposta para operações em lote"""
    success_count: int = Field(..., description="Operações realizadas com sucesso")
    error_count: int = Field(..., description="Operações que falharam")
    total_requested: int = Field(..., description="Total de operações solicitadas")
    success_ids: List[int] = Field(default_factory=list, description="IDs processados com sucesso")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="Detalhes dos erros")
    message: str = Field(..., description="Mensagem de resultado") 
