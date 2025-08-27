from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

from .models import User, RefreshToken
from .config import settings

class AuthService:
    """Servicio de autenticación para manejo de usuarios y tokens"""
    
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generar hash de contraseña"""
        return self.pwd_context.hash(password)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por nombre de usuario"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autenticar usuario con credenciales"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: Optional[str] = None, is_superuser: bool = False) -> User:
        """Crear nuevo usuario"""
        # Verificar que no exista el usuario
        if self.get_user_by_username(username):
            raise ValueError("El nombre de usuario ya existe")
        
        if self.get_user_by_email(email):
            raise ValueError("El email ya está registrado")
        
        # Crear usuario
        hashed_password = self.get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT de acceso"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        
        return encoded_jwt
    
    def create_refresh_token(self, user_id: int) -> str:
        """Crear token de refresh y guardarlo en la base de datos"""
        # Generar token único
        token_data = {
            "user_id": user_id,
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # JWT ID único
        }
        
        expires_delta = timedelta(days=settings.refresh_token_expire_days)
        expire = datetime.utcnow() + expires_delta
        token_data.update({"exp": expire})
        
        # Crear JWT
        refresh_token = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
        
        # Guardar en base de datos
        db_token = RefreshToken(
            token=refresh_token,
            user_id=user_id,
            expires_at=expire
        )
        
        self.db.add(db_token)
        self.db.commit()
        
        return refresh_token
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            
            # Verificar tipo de token
            if payload.get("type") != token_type:
                return None
            
            # Verificar expiración
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            return payload
            
        except JWTError:
            return None
    
    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Obtener refresh token de la base de datos"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False
        ).first()
    
    def revoke_refresh_token(self, token: str) -> bool:
        """Revocar refresh token"""
        db_token = self.get_refresh_token(token)
        if db_token:
            db_token.is_revoked = True
            self.db.commit()
            return True
        return False
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revocar todos los refresh tokens de un usuario"""
        count = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        
        self.db.commit()
        return count
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generar nuevo access token usando refresh token"""
        # Verificar refresh token
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        # Verificar que existe en la base de datos y no está revocado
        db_token = self.get_refresh_token(refresh_token)
        if not db_token or not db_token.is_valid():
            return None
        
        # Obtener usuario
        user = self.get_user_by_id(payload["user_id"])
        if not user or not user.is_active:
            return None
        
        # Revocar el refresh token actual
        self.revoke_refresh_token(refresh_token)
        
        # Crear nuevos tokens
        access_token = self.create_access_token(data={"sub": user.username, "user_id": user.id})
        new_refresh_token = self.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token
        }