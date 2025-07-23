"""
Módulo de Routers - TecnoCursosAI
Organização modular dos endpoints da API
"""

# Importar routers principais
try:
    from .auth import router as auth_router
except ImportError as e:
    print(f"⚠️ Erro ao importar auth_router: {e}")
    auth_router = None

try:
    from .users import router as users_router
except ImportError as e:
    print(f"⚠️ Erro ao importar users_router: {e}")
    users_router = None

try:
    from .projects import router as projects_router
except ImportError as e:
    print(f"⚠️ Erro ao importar projects_router: {e}")
    projects_router = None

try:
    from .files import router as files_router
except ImportError as e:
    print(f"⚠️ Erro ao importar files_router: {e}")
    files_router = None

try:
    from .admin import router as admin_router
except ImportError as e:
    print(f"⚠️ Erro ao importar admin_router: {e}")
    admin_router = None

try:
    from .stats import router as stats_router
except ImportError as e:
    print(f"⚠️ Erro ao importar stats_router: {e}")
    stats_router = None

# Tentar importar router do scenes
try:
    from .scenes import router as scenes_router
    _scenes_available = True
except ImportError:
    scenes_router = None
    _scenes_available = False

# Tentar importar router do avatar se existir
try:
    from .avatar import avatar_router  # Usar o avatar_router exportado
    _avatar_available = True
except ImportError:
    avatar_router = None
    _avatar_available = False

# Tentar importar routers avançados
try:
    from .batch_upload import router as batch_upload
except ImportError:
    batch_upload = None

try:
    from .websocket_router import router as websocket_router
except ImportError:
    websocket_router = None

try:
    from .analytics import router as analytics
except ImportError:
    analytics = None

# Tentar importar routers enterprise
try:
    from .enterprise import router as enterprise_router
except ImportError:
    enterprise_router = None

try:
    from .system_control import router as system_control
except ImportError:
    system_control = None

# Tentar importar routers de vídeo
try:
    from .video_generation import router as video_generation
except ImportError:
    video_generation = None

try:
    from .advanced_video_processing import router as advanced_video_processing
except ImportError:
    advanced_video_processing = None

try:
    from .video_export import router as video_export
except ImportError:
    video_export = None

# Tentar importar routers TTS
try:
    from . import tts
except ImportError:
    tts = None

try:
    from . import tts_advanced
except ImportError:
    tts_advanced = None

# Tentar importar router de admin de áudios
try:
    from . import audio_admin
except ImportError:
    audio_admin = None

__all__ = [
    "auth_router",
    "users_router", 
    "projects_router",
    "files_router",
    "admin_router",
    "stats_router",
    "scenes_router",
    "avatar_router",
    "batch_upload",
    "websocket_router",
    "analytics",
    "enterprise_router",
    "system_control",
    "video_generation",
    "advanced_video_processing",
    "video_export",
    "tts",
    "tts_advanced",
    "audio_admin"
] 