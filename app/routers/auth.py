from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..auth_service import AuthService
from ..schemas import (
    UserLogin, UserResponse, TokenResponse, 
    RefreshTokenRequest, MessageResponse, ErrorResponse
)
from ..config import settings

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), 
                    db: Session = Depends(get_db)):
    """Dependencia para obtener el usuario actual desde el JWT"""
    auth_service = AuthService(db)
    
    # Verificar token
    payload = auth_service.verify_token(credentials.credentials, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario
    user = auth_service.get_user_by_id(payload.get("user_id"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario con credenciales y devuelve tokens JWT",
    responses={
        200: {"description": "Login exitoso", "model": TokenResponse},
        401: {"description": "Credenciales inválidas", "model": ErrorResponse},
        422: {"description": "Error de validación", "model": ErrorResponse}
    }
)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Endpoint para autenticación de usuarios"""
    auth_service = AuthService(db)
    
    # Autenticar usuario
    user = auth_service.authenticate_user(
        user_credentials.username, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    refresh_token = auth_service.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar token de acceso",
    description="Genera un nuevo token de acceso usando un refresh token válido",
    responses={
        200: {"description": "Token renovado exitosamente", "model": TokenResponse},
        401: {"description": "Refresh token inválido", "model": ErrorResponse},
        422: {"description": "Error de validación", "model": ErrorResponse}
    }
)
async def refresh_token(token_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Endpoint para renovar tokens de acceso"""
    auth_service = AuthService(db)
    
    # Renovar tokens
    tokens = auth_service.refresh_access_token(token_request.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Cerrar sesión",
    description="Revoca todos los refresh tokens del usuario autenticado",
    responses={
        200: {"description": "Logout exitoso", "model": MessageResponse},
        401: {"description": "Token inválido", "model": ErrorResponse}
    }
)
async def logout(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Endpoint para cerrar sesión del usuario"""
    auth_service = AuthService(db)
    
    # Revocar todos los refresh tokens del usuario
    revoked_count = auth_service.revoke_all_user_tokens(current_user.id)
    
    return MessageResponse(
        message=f"Sesión cerrada exitosamente. {revoked_count} tokens revocados."
    )

@router.get(
    "/userinfo",
    response_model=UserResponse,
    summary="Información del usuario",
    description="Obtiene la información del usuario autenticado",
    responses={
        200: {"description": "Información del usuario", "model": UserResponse},
        401: {"description": "Token inválido", "model": ErrorResponse}
    }
)
async def get_user_info(current_user = Depends(get_current_user)):
    """Endpoint para obtener información del usuario autenticado"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

# Endpoint adicional para verificar el estado del token
@router.get(
    "/verify-token",
    response_model=MessageResponse,
    summary="Verificar token",
    description="Verifica si el token de acceso es válido",
    responses={
        200: {"description": "Token válido", "model": MessageResponse},
        401: {"description": "Token inválido", "model": ErrorResponse}
    }
)
async def verify_token(current_user = Depends(get_current_user)):
    """Endpoint para verificar la validez del token"""
    return MessageResponse(
        message=f"Token válido para el usuario: {current_user.username}"
    )