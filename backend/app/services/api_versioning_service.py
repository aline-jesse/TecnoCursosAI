"""
Sistema de Versionamento de API e Backwards Compatibility - TecnoCursos AI
========================================================================

Sistema abrangente de versionamento incluindo:
- Múltiplas versões da API em paralelo
- Backwards compatibility automática
- Gerenciamento de deprecation
- Migrações automáticas de dados
- Documentação multi-versão
- Content negotiation inteligente
- Monitoramento de uso por versão

Autor: TecnoCursos AI Team
Data: 2024
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import re
import uuid
from collections import defaultdict
import semver

# Configuração de logging
logger = logging.getLogger(__name__)

class VersionStatus(Enum):
    """Status de uma versão da API"""
    DEVELOPMENT = "development"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"

class BreakingChangeType(Enum):
    """Tipos de mudanças incompatíveis"""
    FIELD_REMOVED = "field_removed"
    FIELD_TYPE_CHANGED = "field_type_changed"
    ENDPOINT_REMOVED = "endpoint_removed"
    REQUIRED_FIELD_ADDED = "required_field_added"
    RESPONSE_FORMAT_CHANGED = "response_format_changed"
    AUTHENTICATION_CHANGED = "authentication_changed"

class CompatibilityLevel(Enum):
    """Níveis de compatibilidade"""
    FULL = "full"              # Totalmente compatível
    PARTIAL = "partial"        # Compatível com adaptações
    BREAKING = "breaking"      # Mudanças incompatíveis
    DEPRECATED = "deprecated"  # Funcionalidade descontinuada

@dataclass
class APIVersion:
    """Definição de versão da API"""
    version: str
    status: VersionStatus
    release_date: datetime
    sunset_date: Optional[datetime]
    description: str
    breaking_changes: List[Dict[str, Any]]
    migration_guide: Optional[str] = None
    usage_count: int = 0
    
@dataclass
class DeprecationNotice:
    """Aviso de deprecação"""
    id: str
    version: str
    feature: str
    deprecated_in: str
    removed_in: Optional[str]
    reason: str
    alternative: Optional[str]
    created_at: datetime

@dataclass
class MigrationRule:
    """Regra de migração entre versões"""
    id: str
    from_version: str
    to_version: str
    field_mappings: Dict[str, str]
    transformations: Dict[str, Callable]
    validation_rules: List[Callable]

@dataclass
class VersionUsageMetrics:
    """Métricas de uso por versão"""
    version: str
    daily_requests: int
    unique_clients: int
    error_rate: float
    avg_response_time: float
    last_used: datetime

class APIVersioningService:
    """
    Serviço de Versionamento de API
    
    Funcionalidades:
    - Gerenciamento de múltiplas versões
    - Migração automática de dados
    - Backwards compatibility
    - Monitoramento de deprecação
    - Documentação multi-versão
    """
    
    def __init__(self):
        # Versões disponíveis
        self.versions: Dict[str, APIVersion] = {}
        self.current_version = "1.0.0"
        self.default_version = "1.0.0"
        
        # Regras de migração
        self.migration_rules: Dict[str, List[MigrationRule]] = defaultdict(list)
        
        # Deprecações
        self.deprecation_notices: List[DeprecationNotice] = []
        
        # Métricas de uso
        self.usage_metrics: Dict[str, VersionUsageMetrics] = {}
        
        # Compatibility matrix
        self.compatibility_matrix: Dict[str, Dict[str, CompatibilityLevel]] = defaultdict(dict)
        
        # Schema definitions por versão
        self.schemas: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Middleware chains por versão
        self.middleware_chains: Dict[str, List[Callable]] = defaultdict(list)
        
        # Inicializar versões padrão
        self._initialize_default_versions()
        
        logger.info("✅ API Versioning Service inicializado")
    
    def _initialize_default_versions(self):
        """Inicializa versões padrão do sistema"""
        
        # Versão 1.0.0 - Inicial
        v1_0_0 = APIVersion(
            version="1.0.0",
            status=VersionStatus.STABLE,
            release_date=datetime(2024, 1, 1),
            sunset_date=None,
            description="Versão inicial da API TecnoCursos AI",
            breaking_changes=[]
        )
        self.versions["1.0.0"] = v1_0_0
        
        # Versão 1.1.0 - Melhorias
        v1_1_0 = APIVersion(
            version="1.1.0",
            status=VersionStatus.STABLE,
            release_date=datetime(2024, 6, 1),
            sunset_date=None,
            description="Adição de funcionalidades de avatar e TTS avançado",
            breaking_changes=[]
        )
        self.versions["1.1.0"] = v1_1_0
        
        # Versão 2.0.0 - Major update
        v2_0_0 = APIVersion(
            version="2.0.0",
            status=VersionStatus.BETA,
            release_date=datetime(2024, 12, 1),
            sunset_date=None,
            description="Versão com IA Guardrails, Compliance e Segurança Avançada",
            breaking_changes=[
                {
                    "type": BreakingChangeType.RESPONSE_FORMAT_CHANGED.value,
                    "description": "Novo formato de resposta com metadados de segurança",
                    "affected_endpoints": ["/api/upload", "/api/generate"]
                },
                {
                    "type": BreakingChangeType.AUTHENTICATION_CHANGED.value,
                    "description": "Autenticação JWT obrigatória para todos os endpoints",
                    "affected_endpoints": ["*"]
                }
            ]
        )
        self.versions["2.0.0"] = v2_0_0
        
        # Configurar compatibilidade
        self._setup_compatibility_matrix()
        
        # Configurar migrações
        self._setup_migration_rules()
    
    def _setup_compatibility_matrix(self):
        """Configura matriz de compatibilidade"""
        versions = ["1.0.0", "1.1.0", "2.0.0"]
        
        for v1 in versions:
            for v2 in versions:
                if v1 == v2:
                    self.compatibility_matrix[v1][v2] = CompatibilityLevel.FULL
                elif semver.compare(v1, v2) < 0:  # v1 é mais antiga
                    # Verificar se é mudança major comparando versões major
                    v1_parsed = semver.VersionInfo.parse(v1)
                    v2_parsed = semver.VersionInfo.parse(v2)
                    if v1_parsed.major != v2_parsed.major:
                        self.compatibility_matrix[v1][v2] = CompatibilityLevel.BREAKING
                    else:
                        self.compatibility_matrix[v1][v2] = CompatibilityLevel.PARTIAL
                else:  # v1 é mais nova
                    self.compatibility_matrix[v1][v2] = CompatibilityLevel.FULL
    
    def _setup_migration_rules(self):
        """Configura regras de migração"""
        
        # Migração 1.0.0 -> 1.1.0
        migration_1_0_to_1_1 = MigrationRule(
            id="migrate_1_0_to_1_1",
            from_version="1.0.0",
            to_version="1.1.0",
            field_mappings={
                "file_url": "media_url",
                "thumbnail": "preview_image"
            },
            transformations={
                "add_avatar_support": lambda data: {**data, "avatar_enabled": False},
                "add_tts_options": lambda data: {**data, "tts_options": {}}
            },
            validation_rules=[]
        )
        self.migration_rules["1.0.0"].append(migration_1_0_to_1_1)
        
        # Migração 1.1.0 -> 2.0.0
        migration_1_1_to_2_0 = MigrationRule(
            id="migrate_1_1_to_2_0",
            from_version="1.1.0",
            to_version="2.0.0",
            field_mappings={
                "response": "data",
                "status": "metadata.status"
            },
            transformations={
                "add_security_metadata": lambda data: {
                    "data": data,
                    "metadata": {
                        "version": "2.0.0",
                        "security_level": "standard",
                        "compliance_checked": True,
                        "timestamp": datetime.now().isoformat()
                    }
                },
                "add_guardrails_info": lambda data: {
                    **data,
                    "guardrails": {
                        "risk_level": "low",
                        "human_oversight": False
                    }
                }
            },
            validation_rules=[]
        )
        self.migration_rules["1.1.0"].append(migration_1_1_to_2_0)
    
    async def negotiate_version(
        self,
        request_headers: Dict[str, str],
        query_params: Dict[str, str]
    ) -> str:
        """
        Negocia versão da API baseada em headers e parâmetros
        
        Prioridade:
        1. Query parameter 'version'
        2. Header 'API-Version'
        3. Header 'Accept' com versioning
        4. Versão padrão
        """
        
        # 1. Query parameter
        if "version" in query_params:
            requested_version = query_params["version"]
            if await self._is_version_available(requested_version):
                return requested_version
        
        # 2. Header API-Version
        api_version_header = request_headers.get("api-version") or request_headers.get("API-Version")
        if api_version_header:
            if await self._is_version_available(api_version_header):
                return api_version_header
        
        # 3. Accept header com versioning
        accept_header = request_headers.get("accept", "")
        version_from_accept = self._extract_version_from_accept(accept_header)
        if version_from_accept and await self._is_version_available(version_from_accept):
            return version_from_accept
        
        # 4. Versão padrão
        return self.default_version
    
    def _extract_version_from_accept(self, accept_header: str) -> Optional[str]:
        """Extrai versão do header Accept"""
        # Formato: application/json; version=1.0.0
        version_pattern = r'version=(\d+\.\d+\.\d+)'
        match = re.search(version_pattern, accept_header)
        return match.group(1) if match else None
    
    async def _is_version_available(self, version: str) -> bool:
        """Verifica se versão está disponível"""
        if version not in self.versions:
            return False
        
        version_obj = self.versions[version]
        
        # Versões sunset não estão disponíveis
        if version_obj.status == VersionStatus.SUNSET:
            return False
        
        # Verificar se passou da data de sunset
        if version_obj.sunset_date and datetime.now() > version_obj.sunset_date:
            return False
        
        return True
    
    async def migrate_request_data(
        self,
        data: Dict[str, Any],
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """Migra dados de request entre versões"""
        
        if from_version == to_version:
            return data
        
        # Encontrar caminho de migração
        migration_path = await self._find_migration_path(from_version, to_version)
        if not migration_path:
            logger.warning(f"Nenhum caminho de migração encontrado: {from_version} -> {to_version}")
            return data
        
        migrated_data = data.copy()
        
        # Aplicar migrações em sequência
        for migration in migration_path:
            migrated_data = await self._apply_migration_rule(migrated_data, migration)
        
        logger.info(f"Dados migrados: {from_version} -> {to_version}")
        return migrated_data
    
    async def migrate_response_data(
        self,
        data: Dict[str, Any],
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """Migra dados de response entre versões"""
        
        # Response migration é o inverso do request
        return await self.migrate_request_data(data, to_version, from_version)
    
    async def _find_migration_path(
        self,
        from_version: str,
        to_version: str
    ) -> List[MigrationRule]:
        """Encontra caminho de migração entre versões"""
        
        # Implementação simplificada - migração direta
        if from_version in self.migration_rules:
            for rule in self.migration_rules[from_version]:
                if rule.to_version == to_version:
                    return [rule]
        
        # Para versões intermediárias, seria necessário um algoritmo de pathfinding
        # Por enquanto, retorna lista vazia se não há migração direta
        return []
    
    async def _apply_migration_rule(
        self,
        data: Dict[str, Any],
        rule: MigrationRule
    ) -> Dict[str, Any]:
        """Aplica regra de migração aos dados"""
        
        migrated_data = data.copy()
        
        # Aplicar mapeamentos de campos
        for old_field, new_field in rule.field_mappings.items():
            if old_field in migrated_data:
                # Suporte para campos aninhados (ex: "metadata.status")
                if "." in new_field:
                    self._set_nested_field(migrated_data, new_field, migrated_data[old_field])
                    del migrated_data[old_field]
                else:
                    migrated_data[new_field] = migrated_data.pop(old_field)
        
        # Aplicar transformações
        for transform_name, transform_func in rule.transformations.items():
            try:
                migrated_data = transform_func(migrated_data)
            except Exception as e:
                logger.error(f"Erro na transformação {transform_name}: {e}")
        
        # Aplicar validações
        for validation in rule.validation_rules:
            try:
                if not validation(migrated_data):
                    logger.warning(f"Validação falhou na migração {rule.id}")
            except Exception as e:
                logger.error(f"Erro na validação: {e}")
        
        return migrated_data
    
    def _set_nested_field(self, data: Dict[str, Any], field_path: str, value: Any):
        """Define campo aninhado usando notação de ponto"""
        parts = field_path.split(".")
        current = data
        
        # Navegar até o penúltimo nível
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Definir valor final
        current[parts[-1]] = value
    
    async def add_deprecation_notice(
        self,
        version: str,
        feature: str,
        deprecated_in: str,
        reason: str,
        alternative: Optional[str] = None,
        removed_in: Optional[str] = None
    ):
        """Adiciona aviso de deprecação"""
        
        notice = DeprecationNotice(
            id=str(uuid.uuid4()),
            version=version,
            feature=feature,
            deprecated_in=deprecated_in,
            removed_in=removed_in,
            reason=reason,
            alternative=alternative,
            created_at=datetime.now()
        )
        
        self.deprecation_notices.append(notice)
        logger.info(f"Deprecação adicionada: {feature} em {deprecated_in}")
    
    async def get_deprecation_warnings(self, version: str) -> List[DeprecationNotice]:
        """Retorna avisos de deprecação para uma versão"""
        return [notice for notice in self.deprecation_notices 
                if notice.version == version]
    
    async def track_version_usage(
        self,
        version: str,
        client_id: Optional[str] = None,
        response_time: Optional[float] = None,
        error_occurred: bool = False
    ):
        """Rastreia uso de versão da API"""
        
        if version not in self.usage_metrics:
            self.usage_metrics[version] = VersionUsageMetrics(
                version=version,
                daily_requests=0,
                unique_clients=0,
                error_rate=0.0,
                avg_response_time=0.0,
                last_used=datetime.now()
            )
        
        metrics = self.usage_metrics[version]
        metrics.daily_requests += 1
        metrics.last_used = datetime.now()
        
        if response_time:
            # Calcular média móvel do tempo de resposta
            current_avg = metrics.avg_response_time
            new_avg = (current_avg * (metrics.daily_requests - 1) + response_time) / metrics.daily_requests
            metrics.avg_response_time = new_avg
        
        if error_occurred:
            # Calcular taxa de erro
            error_count = metrics.error_rate * (metrics.daily_requests - 1)
            metrics.error_rate = (error_count + 1) / metrics.daily_requests
        
        # Atualizar contagem de uso na versão
        if version in self.versions:
            self.versions[version].usage_count += 1
    
    async def create_new_version(
        self,
        version: str,
        description: str,
        status: VersionStatus = VersionStatus.DEVELOPMENT,
        breaking_changes: Optional[List[Dict[str, Any]]] = None
    ) -> APIVersion:
        """Cria nova versão da API"""
        
        if version in self.versions:
            raise ValueError(f"Versão {version} já existe")
        
        new_version = APIVersion(
            version=version,
            status=status,
            release_date=datetime.now(),
            sunset_date=None,
            description=description,
            breaking_changes=breaking_changes or []
        )
        
        self.versions[version] = new_version
        logger.info(f"Nova versão criada: {version}")
        
        return new_version
    
    async def sunset_version(self, version: str, sunset_date: datetime):
        """Programa sunset de uma versão"""
        
        if version not in self.versions:
            raise ValueError(f"Versão {version} não encontrada")
        
        self.versions[version].sunset_date = sunset_date
        self.versions[version].status = VersionStatus.DEPRECATED
        
        logger.info(f"Versão {version} programada para sunset em {sunset_date}")
    
    async def get_compatibility_info(
        self,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """Retorna informações de compatibilidade entre versões"""
        
        compatibility = self.compatibility_matrix.get(from_version, {}).get(
            to_version, CompatibilityLevel.BREAKING
        )
        
        migration_available = bool(await self._find_migration_path(from_version, to_version))
        
        breaking_changes = []
        if to_version in self.versions:
            breaking_changes = self.versions[to_version].breaking_changes
        
        return {
            "from_version": from_version,
            "to_version": to_version,
            "compatibility_level": compatibility.value,
            "migration_available": migration_available,
            "breaking_changes": breaking_changes,
            "deprecation_warnings": await self.get_deprecation_warnings(from_version)
        }
    
    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Retorna informações detalhadas de uma versão"""
        
        if version not in self.versions:
            return None
        
        version_obj = self.versions[version]
        
        return {
            **asdict(version_obj),
            "is_available": asyncio.run(self._is_version_available(version)),
            "usage_metrics": asdict(self.usage_metrics.get(version)) if version in self.usage_metrics else None,
            "deprecation_warnings": asyncio.run(self.get_deprecation_warnings(version))
        }
    
    def get_all_versions(self) -> Dict[str, Dict[str, Any]]:
        """Retorna informações de todas as versões"""
        
        return {
            version: self.get_version_info(version)
            for version in self.versions.keys()
        }
    
    def get_versioning_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de versionamento"""
        
        total_usage = sum(metrics.daily_requests for metrics in self.usage_metrics.values())
        
        version_distribution = {
            version: (metrics.daily_requests / total_usage * 100) if total_usage > 0 else 0
            for version, metrics in self.usage_metrics.items()
        }
        
        deprecated_versions = [
            version for version, info in self.versions.items()
            if info.status == VersionStatus.DEPRECATED
        ]
        
        return {
            "total_versions": len(self.versions),
            "current_version": self.current_version,
            "default_version": self.default_version,
            "total_requests_today": total_usage,
            "version_distribution": version_distribution,
            "deprecated_versions": deprecated_versions,
            "deprecation_notices": len(self.deprecation_notices),
            "migration_rules": sum(len(rules) for rules in self.migration_rules.values())
        }
    
    def generate_openapi_spec(self, version: str) -> Dict[str, Any]:
        """Gera especificação OpenAPI para uma versão específica"""
        
        if version not in self.versions:
            raise ValueError(f"Versão {version} não encontrada")
        
        version_info = self.versions[version]
        
        # Base OpenAPI spec
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "TecnoCursos AI API",
                "version": version,
                "description": version_info.description,
                "contact": {
                    "name": "TecnoCursos AI Support",
                    "email": "support@tecnocursos.ai"
                }
            },
            "servers": [
                {
                    "url": f"https://api.tecnocursos.ai/v{version.split('.')[0]}",
                    "description": f"API v{version}"
                }
            ],
            "paths": {},
            "components": {
                "schemas": self.schemas.get(version, {}),
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
        
        # Adicionar avisos de deprecação
        deprecation_warnings = asyncio.run(self.get_deprecation_warnings(version))
        if deprecation_warnings:
            spec["info"]["x-deprecation-warnings"] = [
                {
                    "feature": notice.feature,
                    "message": notice.reason,
                    "deprecated_in": notice.deprecated_in,
                    "removed_in": notice.removed_in,
                    "alternative": notice.alternative
                }
                for notice in deprecation_warnings
            ]
        
        return spec

# === INSTÂNCIA GLOBAL ===
api_versioning_service = APIVersioningService()

logger.info("✅ API Versioning Service carregado com sucesso") 