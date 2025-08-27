from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import os

from .config import settings
from .models import Base

# Crear el motor de base de datos
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug  # Mostrar queries SQL en modo debug
)

# Crear la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Inicializar la base de datos creando todas las tablas"""
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente")

def get_db() -> Generator[Session, None, None]:
    """Dependencia para obtener una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_test_user():
    """Crear un usuario de prueba para desarrollo"""
    from .auth_service import AuthService
    from .models import UserRole
    
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        
        # Verificar si ya existe el usuario de prueba
        existing_user = auth_service.get_user_by_username("admin")
        if not existing_user:
            # Crear usuario administrador de prueba
            user = auth_service.create_user(
                username="admin",
                email="admin@atomocr.ai",
                password="admin123",
                full_name="Administrador del Sistema",
                role=UserRole.ADMIN,
                is_active=True
            )
            print(f"Usuario de prueba creado: {user.username} (ID: {user.id})")
        else:
            print("Usuario de prueba ya existe")
            
    except Exception as e:
        print(f"Error al crear usuario de prueba: {e}")
    finally:
        db.close()