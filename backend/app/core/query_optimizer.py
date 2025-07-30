"""
Otimizações de Consulta - TecnoCursos AI
Classes e funções para otimizar consultas do banco de dados
"""

from typing import List, Optional, Dict, Any, Type, Union
from sqlalchemy.orm import Session, selectinload, joinedload, contains_eager
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.sql import Select
from dataclasses import dataclass

from ..models import User, Project, FileUpload, Video, Audio, Scene, Asset
from ..core.cache import cached, cache_manager

@dataclass
class QueryOptions:
    """Opções para otimização de consultas"""
    use_cache: bool = True
    cache_ttl: int = 300
    load_relationships: List[str] = None
    select_fields: List[str] = None
    join_tables: List[str] = None

class OptimizedQueries:
    """Classe para consultas otimizadas com eager loading e cache"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @cached(ttl=300, cache_type="project_list")
    async def get_user_projects_optimized(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        include_stats: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Busca projetos do usuário com otimizações:
        - Eager loading de relacionamentos
        - Cache de resultado
        - Estatísticas agregadas em uma consulta
        """
        
        # Query principal com eager loading
        query = (
            select(Project)
            .options(
                selectinload(Project.files),
                selectinload(Project.videos),
                selectinload(Project.scenes),
                joinedload(Project.owner)
            )
            .where(Project.owner_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Project.updated_at.desc())
        )
        
        projects = self.db.execute(query).unique().scalars().all()
        
        result = []
        for project in projects:
            project_data = {
                "id": project.id,
                "uuid": project.uuid,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "is_public": project.is_public,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "owner": {
                    "id": project.owner.id,
                    "username": project.owner.username,
                    "full_name": project.owner.full_name
                }
            }
            
            if include_stats:
                # Estatísticas já carregadas via eager loading
                project_data.update({
                    "total_files": len(project.files),
                    "total_videos": len(project.videos),
                    "total_scenes": len(project.scenes),
                    "last_file_upload": max(
                        (f.uploaded_at for f in project.files), 
                        default=None
                    )
                })
            
            result.append(project_data)
        
        return result
    
    @cached(ttl=600, cache_type="project_detail")
    async def get_project_with_full_details(
        self, 
        project_id: int, 
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Busca projeto com todos os detalhes em uma consulta otimizada
        """
        
        # Query com todos os relacionamentos necessários
        query = (
            select(Project)
            .options(
                selectinload(Project.files).selectinload(FileUpload.videos),
                selectinload(Project.files).selectinload(FileUpload.audios),
                selectinload(Project.videos),
                selectinload(Project.scenes).selectinload(Scene.assets),
                joinedload(Project.owner)
            )
            .where(Project.id == project_id)
        )
        
        # Filtrar por usuário se fornecido
        if user_id:
            query = query.where(
                or_(
                    Project.owner_id == user_id,
                    Project.is_public == True
                )
            )
        
        project = self.db.execute(query).unique().scalar_one_or_none()
        
        if not project:
            return None
        
        # Montar resultado completo
        result = {
            "id": project.id,
            "uuid": project.uuid,
            "name": project.name,
            "description": project.description,
            "slug": project.slug,
            "status": project.status,
            "is_public": project.is_public,
            "category": project.category,
            "tags": project.tags,
            "difficulty_level": project.difficulty_level,
            "estimated_duration": project.estimated_duration,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "owner": {
                "id": project.owner.id,
                "username": project.owner.username,
                "full_name": project.owner.full_name,
                "avatar_url": project.owner.avatar_url
            },
            "files": [
                {
                    "id": file.id,
                    "uuid": file.uuid,
                    "filename": file.filename,
                    "original_filename": file.original_filename,
                    "file_type": file.file_type,
                    "file_size": file.file_size,
                    "status": file.status,
                    "uploaded_at": file.uploaded_at,
                    "videos": [
                        {
                            "id": video.id,
                            "title": video.title,
                            "status": video.status,
                            "duration": video.duration
                        }
                        for video in file.videos
                    ],
                    "audios": [
                        {
                            "id": audio.id,
                            "title": audio.title,
                            "status": audio.status,
                            "duration": audio.duration
                        }
                        for audio in file.audios
                    ]
                }
                for file in project.files
            ],
            "videos": [
                {
                    "id": video.id,
                    "uuid": video.uuid,
                    "title": video.title,
                    "description": video.description,
                    "status": video.status,
                    "duration": video.duration,
                    "resolution": video.resolution,
                    "created_at": video.created_at
                }
                for video in project.videos
            ],
            "scenes": [
                {
                    "id": scene.id,
                    "name": scene.name,
                    "scene_type": scene.scene_type,
                    "duration": scene.duration,
                    "order_index": scene.order_index,
                    "assets_count": len(scene.assets)
                }
                for scene in project.scenes
            ],
            "statistics": {
                "total_files": len(project.files),
                "total_videos": len(project.videos),
                "total_scenes": len(project.scenes),
                "total_duration": sum(
                    v.duration for v in project.videos if v.duration
                ),
                "completed_videos": len([
                    v for v in project.videos if v.status == "completed"
                ])
            }
        }
        
        return result
    
    async def get_user_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """
        Busca dados do dashboard em consultas otimizadas
        """
        
        # Estatísticas básicas em uma consulta
        stats_query = (
            select(
                func.count(Project.id).label('total_projects'),
                func.count(
                    case([(Project.status == 'completed', 1)])
                ).label('completed_projects'),
                func.count(
                    case([(Project.is_public == True, 1)])
                ).label('public_projects')
            )
            .where(Project.owner_id == user_id)
        )
        
        stats_result = self.db.execute(stats_query).first()
        
        # Projetos recentes com informações básicas
        recent_projects_query = (
            select(Project)
            .options(joinedload(Project.owner))
            .where(Project.owner_id == user_id)
            .order_by(Project.updated_at.desc())
            .limit(5)
        )
        
        recent_projects = self.db.execute(recent_projects_query).unique().scalars().all()
        
        # Arquivos recentes
        recent_files_query = (
            select(FileUpload)
            .options(joinedload(FileUpload.project))
            .where(FileUpload.user_id == user_id)
            .order_by(FileUpload.uploaded_at.desc())
            .limit(10)
        )
        
        recent_files = self.db.execute(recent_files_query).unique().scalars().all()
        
        return {
            "statistics": {
                "total_projects": stats_result.total_projects,
                "completed_projects": stats_result.completed_projects,
                "public_projects": stats_result.public_projects,
                "completion_rate": (
                    stats_result.completed_projects / stats_result.total_projects * 100
                    if stats_result.total_projects > 0 else 0
                )
            },
            "recent_projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status,
                    "updated_at": p.updated_at
                }
                for p in recent_projects
            ],
            "recent_files": [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "file_type": f.file_type,
                    "uploaded_at": f.uploaded_at,
                    "project_name": f.project.name if f.project else None
                }
                for f in recent_files
            ]
        }
    
    async def search_projects_optimized(
        self,
        query: str,
        user_id: Optional[int] = None,
        public_only: bool = False,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Busca otimizada de projetos com filtros
        """
        
        # Construir query base
        base_query = select(Project).options(joinedload(Project.owner))
        
        # Aplicar filtros
        conditions = []
        
        if query:
            conditions.append(
                or_(
                    Project.name.ilike(f"%{query}%"),
                    Project.description.ilike(f"%{query}%"),
                    Project.tags.ilike(f"%{query}%")
                )
            )
        
        if user_id and not public_only:
            conditions.append(Project.owner_id == user_id)
        elif public_only:
            conditions.append(Project.is_public == True)
        
        if category:
            conditions.append(Project.category == category)
        
        if difficulty:
            conditions.append(Project.difficulty_level == difficulty)
        
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Query para contagem total
        count_query = select(func.count()).select_from(
            base_query.subquery()
        )
        
        total_count = self.db.execute(count_query).scalar()
        
        # Query paginada
        projects_query = (
            base_query
            .order_by(Project.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        projects = self.db.execute(projects_query).unique().scalars().all()
        
        return {
            "projects": [
                {
                    "id": p.id,
                    "uuid": p.uuid,
                    "name": p.name,
                    "description": p.description,
                    "category": p.category,
                    "difficulty_level": p.difficulty_level,
                    "is_public": p.is_public,
                    "created_at": p.created_at,
                    "owner": {
                        "username": p.owner.username,
                        "full_name": p.owner.full_name
                    }
                }
                for p in projects
            ],
            "pagination": {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total_count,
                "has_prev": skip > 0
            }
        }

# Helper functions para uso em routers
async def get_optimized_queries(db: Session) -> OptimizedQueries:
    """Factory function para OptimizedQueries"""
    return OptimizedQueries(db)

# Cache invalidation helpers
async def invalidate_user_cache(user_id: int):
    """Invalida cache relacionado ao usuário"""
    patterns = [
        f"user:{user_id}:*",
        f"proj:*:user:{user_id}:*",
        "search:*"  # Invalidar buscas também
    ]
    
    for pattern in patterns:
        await cache_manager.clear_pattern(pattern)

async def invalidate_project_cache(project_id: int, user_id: int):
    """Invalida cache relacionado ao projeto"""
    patterns = [
        f"proj:{project_id}:*",
        f"user:{user_id}:*",
        "search:*"
    ]
    
    for pattern in patterns:
        await cache_manager.clear_pattern(pattern)
