"""
Sistema de autenticação JWT para TecnoCursos AI
Inclui hash de senhas, geração de tokens e verificação
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import User
from .schemas import UserCreate

settings = get_settings()

# Configuração para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração para JWT
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class AuthManager:
    """Gerenciador de autenticação"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_expiration_hours * 60
        self.oauth2_scheme = oauth2_scheme
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar senha fornecida contra hash armazenado"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Gerar hash da senha"""
        return pwd_context.hash(password)
    
    def create_access_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """Criar token JWT de acesso"""
        to_encode = {"sub": str(user_id)}
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode["exp"] = expire
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: int) -> str:
        """Criar token JWT de refresh (7 dias)"""
        to_encode = {"sub": str(user_id)}
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode["exp"] = expire
        to_encode["type"] = "refresh"
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def update_last_login(self, db: Session, user: User) -> None:
        """Atualizar timestamp de último login"""
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verificar e decodificar token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Autenticar usuário com email e senha"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Buscar usuário por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, db: Session, email: str, username: str, password: str, 
                   full_name: Optional[str] = None) -> User:
        """Criar novo usuário"""
        hashed_password = self.get_password_hash(password)
        
        db_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def register_user(self, db: Session, user_data) -> User:
        """Registrar novo usuário"""
        # Verificar se email já existe
        existing_user = self.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já registrado"
            )
        
        # Verificar se username já existe
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já existe"
            )
        
        # Criar usuário
        return self.create_user(
            db=db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> dict:
        """Renovar access token usando refresh token"""
        try:
            # Verificar refresh token
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token inválido"
                )
            
            # Verificar se usuário existe
            user = self.get_user_by_id(db, int(user_id))
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário não encontrado ou inativo"
                )
            
            # Criar novo access token
            access_token = self.create_access_token(user.id)
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )

# Instância global do gerenciador de autenticação
auth_manager = AuthManager()

# Funções auxiliares para facilitar importação
def get_password_hash(password: str) -> str:
    """Função auxiliar para hash de senha"""
    return auth_manager.get_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Função auxiliar para verificação de senha"""
    return auth_manager.verify_password(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Função auxiliar para criação de token"""
    return auth_manager.create_access_token(data.get("sub"), expires_delta)

def create_refresh_token(data: dict) -> str:
    """Função auxiliar para criação de refresh token"""
    return auth_manager.create_refresh_token(data.get("sub"))

def create_tokens_for_user(user: User) -> dict:
    """Criar tokens de acesso e refresh para usuário"""
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obter usuário atual a partir do token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extrair token do header Authorization
        token = credentials.credentials
        
        # Verificar e decodificar token
        payload = auth_manager.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        # Extrair user_id do payload
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Buscar usuário no banco
    user = auth_manager.get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception
    
    # Verificar se usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency para obter usuário ativo atual
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency para obter usuário admin atual
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency para obter usuário atual (opcional)
    Retorna None se não houver token válido
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token)
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = auth_manager.get_user_by_id(db, int(user_id))
        if user is None or not user.is_active:
            return None
        
        return user
        
    except JWTError:
        return None

def verify_token_type(token: str, expected_type: str = "access") -> bool:
    """
    Verificar tipo do token (access ou refresh)
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_type = payload.get("type", "access")
        return token_type == expected_type
    except JWTError:
        return False 
        return False 