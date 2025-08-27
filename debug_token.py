#!/usr/bin/env python3
"""
Script de debug para verificar la generación y validación de tokens JWT
"""

import sys
sys.path.append('.')

from app.auth_service import AuthService
from app.database import get_db
from app.config import settings
from jose import jwt
from datetime import datetime, timedelta
import json

def debug_token_creation():
    """Debug de creación y validación de tokens"""
    print("=== DEBUG TOKEN CREATION ===")
    print(f"SECRET_KEY: {settings.secret_key[:20]}...")
    print(f"ALGORITHM: {settings.algorithm}")
    print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.access_token_expire_minutes}")
    print(f"REFRESH_TOKEN_EXPIRE_DAYS: {settings.refresh_token_expire_days}")
    print()
    
    # Obtener sesión de base de datos
    db = next(get_db())
    auth_service = AuthService(db)
    
    # Crear token de prueba
    test_data = {"sub": "admin", "user_id": 1}
    token = auth_service.create_access_token(test_data)
    
    print(f"Token generado: {token[:50]}...")
    print()
    
    # Decodificar token manualmente
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print("Payload decodificado:")
        print(json.dumps(payload, indent=2, default=str))
        print()
        
        # Verificar expiración
        exp_timestamp = payload.get('exp')
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            now = datetime.utcnow()
            print(f"Token expira en: {exp_datetime}")
            print(f"Hora actual: {now}")
            print(f"Tiempo restante: {exp_datetime - now}")
            print(f"¿Token expirado?: {now > exp_datetime}")
        print()
        
    except Exception as e:
        print(f"Error decodificando token: {e}")
        return
    
    # Verificar con auth_service
    verified_payload = auth_service.verify_token(token, "access")
    if verified_payload:
        print("✅ Token verificado exitosamente por auth_service")
        print(f"Payload verificado: {verified_payload}")
    else:
        print("❌ Token NO verificado por auth_service")
    
    print()
    
    # Probar autenticación de usuario
    user = auth_service.authenticate_user("admin", "admin123")
    if user:
        print(f"✅ Usuario autenticado: {user.username} (ID: {user.id})")
        print(f"Usuario activo: {user.is_active}")
        print(f"Rol: {user.role}")
    else:
        print("❌ Usuario NO autenticado")
    
    db.close()

if __name__ == "__main__":
    debug_token_creation()