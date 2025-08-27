from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

# Enums
class UserRoleEnum(str, Enum):
    """Enum para roles de usuario en esquemas Pydantic"""
    ADMIN = "admin"
    USER = "user"

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

class UserRegister(BaseModel):
    """Esquema para registro de usuarios por administradores"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña del usuario")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del usuario")
    role: UserRoleEnum = Field(..., description="Rol del usuario (admin o user)")
    active: bool = Field(True, description="Estado activo del usuario")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('El username solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "nuevo_usuario",
                "email": "nuevo@ejemplo.com",
                "password": "contraseña123",
                "full_name": "Nuevo Usuario",
                "role": "user",
                "active": True
            }
        }

class UserResponse(BaseModel):
    """Esquema para respuesta de información de usuario"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
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
                "role": "admin",
                "is_active": True,
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

# Esquemas para clientes
class ClientCreate(BaseModel):
    """Esquema para creación de cliente"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del cliente")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del cliente")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('El nombre del cliente no puede estar vacío')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Mi Aplicación Web",
                "description": "Cliente para acceder a los recursos de mi aplicación web"
            }
        }

class ClientResponse(BaseModel):
    """Esquema para respuesta de información de cliente"""
    id: int
    name: str
    description: Optional[str] = None
    client_id: str
    client_secret: str
    is_active: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Mi Aplicación Web",
                "description": "Cliente para acceder a los recursos de mi aplicación web",
                "client_id": "abc123def456ghi789jkl012mno345pq",
                "client_secret": "xyz789uvw456rst123opq890lmn567hij234efg901bcd678",
                "is_active": True,
                "user_id": 1,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "last_used": None
            }
        }

class ClientUpdate(BaseModel):
    """Esquema para actualización de cliente"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del cliente")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del cliente")
    is_active: Optional[bool] = Field(None, description="Estado activo del cliente")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('El nombre del cliente no puede estar vacío')
        return v.strip() if v else v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Mi Aplicación Web Actualizada",
                "description": "Descripción actualizada del cliente",
                "is_active": True
            }
        }

class ClientListResponse(BaseModel):
    """Esquema para respuesta de lista de clientes"""
    id: int
    name: str
    description: Optional[str] = None
    client_id: str
    is_active: bool
    user_id: int
    created_at: datetime
    last_used: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Mi Aplicación Web",
                "description": "Cliente para acceder a los recursos de mi aplicación web",
                "client_id": "abc123def456ghi789jkl012mno345pq",
                "is_active": True,
                "user_id": 1,
                "created_at": "2024-01-15T10:30:00Z",
                "last_used": None
            }
        }