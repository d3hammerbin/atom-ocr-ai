#!/usr/bin/env python3
"""
Script para simular el flujo exacto de Postman: Login -> UserInfo
"""

import sys
sys.path.append('.')

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_postman_flow():
    """Simular el flujo exacto de Postman"""
    print("=== SIMULANDO FLUJO DE POSTMAN ===")
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Paso 1: Login
    print("1. Realizando login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get("access_token")
            refresh_token = login_result.get("refresh_token")
            
            print(f"✅ Login exitoso")
            print(f"Access Token: {access_token[:50]}...")
            print(f"Refresh Token: {refresh_token[:50]}...")
            print(f"Token Type: {login_result.get('token_type')}")
            print(f"Expires In: {login_result.get('expires_in')} segundos")
            print()
            
            # Paso 2: Inmediatamente hacer userinfo
            print("2. Obteniendo información del usuario (inmediatamente después del login)...")
            
            userinfo_response = requests.get(
                f"{BASE_URL}/api/v1/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Status Code: {userinfo_response.status_code}")
            
            if userinfo_response.status_code == 200:
                userinfo_result = userinfo_response.json()
                print(f"✅ UserInfo exitoso")
                print(f"Usuario: {userinfo_result.get('username')}")
                print(f"Email: {userinfo_result.get('email')}")
                print(f"Rol: {userinfo_result.get('role')}")
            else:
                print(f"❌ UserInfo falló")
                print(f"Response: {userinfo_response.text}")
                
                # Debug del token
                print("\n=== DEBUG DEL TOKEN ===")
                print(f"Token enviado: {access_token[:100]}...")
                
                # Verificar si el token es válido usando verify-token endpoint
                verify_response = requests.get(
                    f"{BASE_URL}/api/v1/verify-token",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                print(f"Verify Token Status: {verify_response.status_code}")
                print(f"Verify Token Response: {verify_response.text}")
            
        else:
            print(f"❌ Login falló")
            print(f"Response: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está el servidor ejecutándose?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_postman_flow()