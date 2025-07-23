
"""
Fallback service para Redis quando não disponível
"""

import json
from typing import Any, Optional
from datetime import datetime, timedelta

class FallbackRedisService:
    """Serviço de cache em memória como fallback para Redis"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if key in self._cache:
            # Verificar expiração
            if key in self._expiry and datetime.now() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Define valor no cache"""
        try:
            self._cache[key] = value
            if ex:
                self._expiry[key] = datetime.now() + timedelta(seconds=ex)
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        return key in self._cache
    
    def flushall(self) -> bool:
        """Limpa todo o cache"""
        self._cache.clear()
        self._expiry.clear()
        return True

# Instância global
fallback_redis = FallbackRedisService()
