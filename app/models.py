from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import secrets
import string
import hashlib
import hmac

Base = declarative_base()

class UserRole(enum.Enum):
    """Enum para roles de usuario"""
    ADMIN = "admin"
    USER = "user"

class User(Base):
    """Modelo de usuario para autenticación"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relación con clientes
    clients = relationship("Client", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class RefreshToken(Base):
    """Modelo para tokens de refresh"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False)  # Foreign key a users.id
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"
    
    def is_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Verifica si el token es válido (no expirado y no revocado)"""
        return not self.is_expired() and not self.is_revoked


class Client(Base):
    """Modelo de cliente para credenciales de identificación"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    client_id = Column(String(32), unique=True, index=True, nullable=False)
    client_secret = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relación con el usuario creador
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="clients")
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', client_id='{self.client_id}', user_id={self.user_id})>"
    
    @staticmethod
    def generate_client_id() -> str:
        """Genera un client_id único de 32 caracteres"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    @staticmethod
    def generate_client_secret() -> str:
        """Genera un client_secret único de 64 caracteres"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation.replace('"', '').replace("'", '')) for _ in range(64))
    
    @staticmethod
    def hash_client_secret(client_secret: str) -> str:
        """Genera un hash seguro del client_secret usando SHA-256"""
        return hashlib.sha256(client_secret.encode('utf-8')).hexdigest()
    
    def verify_client_secret(self, client_secret: str) -> bool:
        """Verifica si el client_secret proporcionado coincide con el almacenado"""
        # Si el client_secret almacenado ya está hasheado (64 caracteres hex)
        if len(self.client_secret) == 64 and all(c in '0123456789abcdef' for c in self.client_secret.lower()):
            return hmac.compare_digest(self.client_secret, self.hash_client_secret(client_secret))
        # Si está en texto plano (para compatibilidad con datos existentes)
        return hmac.compare_digest(self.client_secret, client_secret)
    
    def set_client_secret(self, client_secret: str, hash_secret: bool = True) -> None:
        """Establece el client_secret, opcionalmente hasheándolo"""
        if hash_secret:
            self.client_secret = self.hash_client_secret(client_secret)
        else:
            self.client_secret = client_secret


class IdsWarehouse(Base):
    """Modelo para almacenamiento de imágenes de credenciales de identificación"""
    __tablename__ = "ids_warehouse"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Información del archivo
    filename = Column(String(255), nullable=False, index=True)  # Nombre post UUID y conversión
    original_filename = Column(String(255), nullable=True)  # Nombre original del archivo
    
    # Metadatos de clasificación
    credential_side = Column(Enum(enum.Enum('CredentialSide', 'FRONT BACK')), nullable=False)
    document_type = Column(Integer, nullable=False)  # 1, 2, 3
    
    # Estado del procesamiento
    is_processed = Column(Boolean, default=False)
    is_rejected = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)  # Soft delete
    
    # Metadatos temporales
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("User")
    client = relationship("Client")
    
    def __repr__(self):
        return f"<IdsWarehouse(id={self.id}, filename='{self.filename}', user_id={self.user_id}, client_id={self.client_id})>"