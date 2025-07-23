"""
Router de Autenticação - TecnoCursosAI
Endpoints para login, registro, refresh token e logout
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..auth import auth_manager, get_current_user_optional
from ..schemas import UserCreate, UserResponse
from ..models import User
from ..logger import get_logger

logger = get_logger("auth_router")

router = APIRouter(
    tags=["🔐 Autenticação"],
    responses={404: {"description": "Não encontrado"}}
)

# Schemas específicos para autenticação
class LoginRequest(BaseModel):
    """Schema para request de login"""
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    """Schema para request de registro"""
    full_name: str
    email: EmailStr
    password: str
    username: str

class LoginResponse(BaseModel):
    """Schema para resposta de login"""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """Schema para refresh token"""
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    """Schema para response de refresh token"""
    access_token: str
    token_type: str

class MessageResponse(BaseModel):
    """Schema para respostas simples"""
    message: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registrar novo usuário
    
    - **name**: Nome completo do usuário
    - **email**: Email único do usuário
    - **password**: Senha (mínimo 8 caracteres)
    - **phone**: Telefone (opcional)
    - **company**: Empresa (opcional)
    """
    
    try:
        logger.info("Tentativa de registro", email=user_data.email)
        
        user = auth_manager.register_user(db, user_data)
        
        logger.info("Usuário registrado com sucesso", user_id=user.id, email=user.email)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro no registro", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no registro"
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Fazer login com email e senha
    
    - **email**: Email do usuário
    - **password**: Senha do usuário
    
    Retorna tokens de acesso e renovação
    """
    
    try:
        logger.info(f"Tentativa de login para: {login_data.email}")
        
        # Autenticar usuário usando auth_manager
        user = auth_manager.authenticate_user(db, login_data.email, login_data.password)
        
        if not user:
            logger.warning(f"Login falhou para: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Criar tokens usando auth_manager
        access_token = auth_manager.create_access_token(user.id)
        refresh_token = auth_manager.create_refresh_token(user.id)
        
        logger.info(f"Login realizado com sucesso para: {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no login"
        )

@router.post("/login/form", response_model=LoginResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login usando formulário OAuth2 (compatibilidade com Swagger UI)
    
    - **username**: Email do usuário
    - **password**: Senha do usuário
    """
    
    # Usar endpoint de login normal
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    return await login(login_data, db)

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renovar token de acesso usando refresh token
    
    - **refresh_token**: Token de renovação válido
    """
    
    try:
        logger.info("Tentativa de refresh token")
        
        tokens = auth_manager.refresh_access_token(db, refresh_data.refresh_token)
        
        logger.info("Token renovado com sucesso")
        
        return RefreshTokenResponse(
            access_token=tokens["access_token"],
            token_type=tokens["token_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro no refresh token", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no refresh token"
        )

@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user_optional)
):
    """
    Fazer logout (invalidar token)
    
    Nota: Atualmente o logout é do lado cliente (remover token).
    Em uma implementação completa, seria necessário uma blacklist de tokens.
    """
    
    logger.info("Logout realizado", user_id=current_user.id, email=current_user.email)
    
    return MessageResponse(message="Logout realizado com sucesso")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obter informações do usuário atual
    
    Retorna os dados do usuário autenticado
    """
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    
    logger.info("Informações do usuário solicitadas", user_id=current_user.id)
    
    return UserResponse.from_orm(current_user)

@router.post("/validate", response_model=UserResponse)
async def validate_token(
    current_user: User = Depends(get_current_user_optional)
):
    """
    Validar token de acesso
    
    Retorna informações do usuário se o token for válido
    """
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    logger.info("Token validado com sucesso", user_id=current_user.id)
    
    return UserResponse.from_orm(current_user)

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    current_user: User = Depends(get_current_user_optional)
):
    """
    Alterar senha do usuário
    
    Endpoint para alteração de senha (implementação futura)
    """
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    
    logger.info("Alteração de senha solicitada", user_id=current_user.id)
    
    return MessageResponse(message="Funcionalidade de alteração de senha em desenvolvimento")

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password():
    """
    Solicitar redefinição de senha
    
    Endpoint para recuperação de senha (implementação futura)
    """
    
    logger.info("Solicitação de redefinição de senha")
    
    return MessageResponse(message="Funcionalidade de recuperação de senha em desenvolvimento") 