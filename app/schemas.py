from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Esquemas para autenticación
class UserLogin(BaseModel):
    """Esquema para login de usuario"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }

class UserCreate(BaseModel):
    """Esquema para creación de usuario"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña del usuario")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "usuario_ejemplo",
                "email": "usuario@ejemplo.com",
                "password": "contraseña123",
                "full_name": "Usuario de Ejemplo"
            }
        }

class UserResponse(BaseModel):
    """Esquema para respuesta de información de usuario"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@atomocr.ai",
                "full_name": "Administrador del Sistema",
                "is_active": True,
                "is_superuser": True,
                "created_at": "2024-01-15T10:30:00Z",
                "last_login": "2024-01-15T15:45:00Z"
            }
        }

class TokenResponse(BaseModel):
    """Esquema para respuesta de tokens"""
    access_token: str = Field(..., description="Token JWT de acceso")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }

class RefreshTokenRequest(BaseModel):
    """Esquema para solicitud de refresh token"""
    refresh_token: str = Field(..., description="Token de refresh válido")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

class MessageResponse(BaseModel):
    """Esquema para respuestas de mensajes simples"""
    message: str = Field(..., description="Mensaje de respuesta")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operación realizada exitosamente"
            }
        }

class ErrorResponse(BaseModel):
    """Esquema para respuestas de error"""
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Descripción del error")
    details: Optional[str] = Field(None, description="Detalles adicionales del error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "AUTHENTICATION_ERROR",
                "message": "Credenciales inválidas",
                "details": "El usuario o contraseña proporcionados son incorrectos"
            }
        }