"""
Sistema de Autenticação Seguro - TecnoCursos AI
Implementa validação robusta de JWT com todas as boas práticas de segurança
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel

class TokenData(BaseModel):
    """Dados extraídos do token JWT"""
    user_id: int
    email: str
    username: str
    is_admin: bool = False
    exp: int
    iat: int
    jti: str  # JWT ID único
    
class SecureAuthManager:
    """Gerenciador de autenticação seguro"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.blacklisted_tokens = set()  # Em produção, usar Redis
        
    def create_password_hash(self, password: str) -> str:
        """Cria hash seguro da senha"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica senha"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        user_id: int, 
        email: str, 
        username: str,
        is_admin: bool = False,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Cria token JWT seguro"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        
        # JWT ID único para rastreamento
        jti = secrets.token_urlsafe(32)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "username": username,
            "is_admin": is_admin,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "iss": "TecnoCursosAI",  # Issuer
            "aud": "TecnoCursosAI-Users"  # Audience
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_token(self, token: str) -> TokenData:
        """Valida token JWT com verificações robustas"""
        try:
            # Verificar se token está na blacklist
            if token in self.blacklisted_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token foi revogado"
                )
            
            # Decodificar e validar token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_aud": True
                },
                issuer="TecnoCursosAI",
                audience="TecnoCursosAI-Users"
            )
            
            # Validar campos obrigatórios
            required_fields = ["user_id", "email", "username", "jti"]
            for field in required_fields:
                if field not in payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Token inválido: campo {field} ausente"
                    )
            
            # Verificar se token não expirou (verificação extra)
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado"
                )
            
            return TokenData(**payload)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Erro na validação do token"
            )
    
    def blacklist_token(self, token: str) -> None:
        """Adiciona token à blacklist (logout)"""
        self.blacklisted_tokens.add(token)
    
    def create_refresh_token(self, user_id: int) -> str:
        """Cria refresh token de longa duração"""
        expire = datetime.utcnow() + timedelta(days=30)
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_refresh_token(self, token: str) -> int:
        """Valida refresh token e retorna user_id"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de refresh inválido"
                )
            
            return payload["user_id"]
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )

# Instância global segura
secure_auth = None

def get_secure_auth(secret_key: str) -> SecureAuthManager:
    """Factory function para auth manager"""
    global secure_auth
    if secure_auth is None:
        secure_auth = SecureAuthManager(secret_key)
    return secure_auth
