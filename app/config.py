from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno"""
    
    # Configuración de la base de datos
    database_url: str = "sqlite:///./atom_ocr_ai.db"
    
    # Configuración JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 horas para facilitar pruebas
    refresh_token_expire_days: int = 30  # 30 días
    
    # Configuración de la aplicación
    app_name: str = "Atom OCR AI"
    debug: bool = True
    
    # Configuración de seguridad
    bcrypt_rounds: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignorar campos extra del .env

# Instancia global de configuración
settings = Settings()