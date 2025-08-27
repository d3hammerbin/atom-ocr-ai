#!/usr/bin/env python3
"""
Script para probar la nueva colección de Postman mejorada
Simula el comportamiento exacto de la colección con debugging mejorado
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

# Variables de entorno simuladas (como en Postman)
postman_environment = {
    "base_url": BASE_URL,
    "username": USERNAME,
    "password": PASSWORD,
    "access_token": "",
    "refresh_token": ""
}

def log_section(title):
    """Simula los logs de consola de Postman"""
    print(f"\n=== {title} ===")

def simulate_login():
    """Simula el endpoint de Login con la nueva colección"""
    log_section("PRE-REQUEST LOGIN")
    print("Limpiando tokens anteriores...")
    postman_environment["access_token"] = ""
    postman_environment["refresh_token"] = ""
    print("Tokens anteriores limpiados.")
    
    # Realizar login
    login_data = {
        "username": postman_environment["username"],
        "password": postman_environment["password"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    response = requests.post(f"{postman_environment['base_url']}/login", 
                           json=login_data, headers=headers)
    response_time = int((time.time() - start_time) * 1000)
    
    log_section("RESPONSE LOGIN")
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {response_time}ms")
    
    if response.status_code == 200:
        print("✅ LOGIN EXITOSO")
        
        try:
            response_data = response.json()
        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
            print(f"Response text: {response.text}")
            return False
        
        # Validar estructura de respuesta
        required_fields = ['access_token', 'refresh_token', 'token_type', 'expires_in']
        for field in required_fields:
            if field not in response_data:
                print(f"❌ Missing field: {field}")
                return False
        
        # Validar que los tokens no estén vacíos
        if not response_data['access_token'] or not response_data['refresh_token']:
            print("❌ Tokens are empty")
            return False
        
        # Guardar tokens en variables de entorno
        print("Guardando tokens en variables de entorno...")
        postman_environment["access_token"] = response_data["access_token"]
        postman_environment["refresh_token"] = response_data["refresh_token"]
        
        # Log información del token
        print(f"Access Token (primeros 50 chars): {response_data['access_token'][:50]}...")
        print(f"Refresh Token (primeros 50 chars): {response_data['refresh_token'][:50]}...")
        print(f"Token Type: {response_data['token_type']}")
        print(f"Expires In: {response_data['expires_in']} segundos")
        
        # Verificar que se guardaron correctamente
        saved_access_token = postman_environment["access_token"]
        saved_refresh_token = postman_environment["refresh_token"]
        
        if saved_access_token == response_data["access_token"] and saved_refresh_token == response_data["refresh_token"]:
            print("✅ Tokens guardados y verificados correctamente")
            return True
        else:
            print("❌ Error guardando tokens")
            return False
            
    elif response.status_code == 401:
        print("❌ LOGIN FALLÓ - Credenciales inválidas")
        print(f"Response: {response.text}")
        return False
        
    elif response.status_code == 422:
        print("❌ LOGIN FALLÓ - Error de validación")
        print(f"Response: {response.text}")
        return False
        
    else:
        print("❌ LOGIN FALLÓ - Error inesperado")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def simulate_user_info():
    """Simula el endpoint de User Info con la nueva colección"""
    log_section("PRE-REQUEST USER INFO")
    
    # Verificar variables de entorno
    token = postman_environment.get("access_token")
    refresh_token = postman_environment.get("refresh_token")
    base_url = postman_environment.get("base_url")
    
    print(f"Base URL: {base_url}")
    print(f"Access Token disponible: {'SÍ' if token else 'NO'}")
    print(f"Refresh Token disponible: {'SÍ' if refresh_token else 'NO'}")
    
    if token:
        print(f"Token (primeros 50 chars): {token[:50]}...")
        print(f"Token (últimos 20 chars): ...{token[-20:]}")
        print(f"Token length: {len(token)}")
    else:
        print("⚠️ WARNING: No access token found!")
        print("💡 SUGERENCIA: Ejecuta el endpoint de Login primero")
        return False
    
    # Debug: Mostrar todas las variables de entorno
    print("--- Variables de entorno ---")
    for key, value in postman_environment.items():
        if 'token' in key:
            print(f"  {key}: {'SET (' + str(len(value)) + ' chars)' if value else 'EMPTY'}")
        else:
            print(f"  {key}: {value}")
    print("--- Fin variables de entorno ---")
    
    # Realizar solicitud
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    response = requests.get(f"{base_url}/userinfo", headers=headers)
    response_time = int((time.time() - start_time) * 1000)
    
    log_section("RESPONSE USER INFO")
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {response_time}ms")
    
    # Verificar headers
    content_type = response.headers.get('content-type', 'N/A')
    print(f"Content-Type: {content_type}")
    
    if response.status_code == 200:
        print("✅ USER INFO OBTENIDA EXITOSAMENTE")
        
        try:
            response_data = response.json()
        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
            print(f"Response text: {response.text}")
            return False
        
        print(f"User info: {json.dumps(response_data, indent=2)}")
        
        # Validar estructura de respuesta
        required_fields = ['id', 'username', 'email', 'role']
        for field in required_fields:
            if field not in response_data:
                print(f"❌ Missing field: {field}")
                return False
        
        print("✅ User info retrieved successfully")
        return True
        
    elif response.status_code == 401:
        print("🚫 TOKEN EXPIRADO O INVÁLIDO")
        print(f"Response Body: {response.text}")
        
        # Verificar qué token se intentó usar
        used_token = postman_environment.get("access_token")
        print(f"Token que se intentó usar: {'SET (' + str(len(used_token)) + ' chars)' if used_token else 'NO TOKEN'}")
        
        if used_token:
            print(f"Token (primeros 50 chars): {used_token[:50]}...")
            print(f"Token (últimos 20 chars): ...{used_token[-20:]}")
        
        print("💡 SUGERENCIA: Ejecuta el endpoint de Login nuevamente para obtener un token fresco")
        return False
        
    else:
        print("❌ ERROR INESPERADO")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        return False

def simulate_refresh_token():
    """Simula el endpoint de Refresh Token con la nueva colección"""
    log_section("PRE-REQUEST REFRESH TOKEN")
    
    refresh_token = postman_environment.get("refresh_token")
    current_access_token = postman_environment.get("access_token")
    
    print(f"Refresh Token disponible: {'SÍ' if refresh_token else 'NO'}")
    print(f"Access Token actual disponible: {'SÍ' if current_access_token else 'NO'}")
    
    if not refresh_token:
        print("⚠️ WARNING: No refresh token found. Please login first.")
        return False
    else:
        print(f"Refresh Token (primeros 50 chars): {refresh_token[:50]}...")
    
    # Realizar solicitud
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{postman_environment['base_url']}/refresh", 
                           json=refresh_data, headers=headers)
    
    log_section("RESPONSE REFRESH TOKEN")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ TOKEN REFRESH EXITOSO")
        
        response_data = response.json()
        old_token = postman_environment.get("access_token")
        
        # Actualizar el access token
        postman_environment["access_token"] = response_data["access_token"]
        
        print(f"Nuevo Access Token (primeros 50 chars): {response_data['access_token'][:50]}...")
        print(f"Token Type: {response_data['token_type']}")
        print(f"Expires In: {response_data['expires_in']} segundos")
        
        # Verificar que el token cambió
        if old_token and old_token != response_data["access_token"]:
            print("✅ Token actualizado correctamente (es diferente al anterior)")
        elif not old_token:
            print("✅ Primer token obtenido")
        else:
            print("⚠️ WARNING: El nuevo token es igual al anterior")
        
        # Verificar que se guardó correctamente
        if postman_environment["access_token"] == response_data["access_token"]:
            print("✅ New access token saved")
            return True
        else:
            print("❌ Error saving new token")
            return False
            
    else:
        print("❌ TOKEN REFRESH FALLÓ")
        print(f"Response Body: {response.text}")
        return False

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DE LA NUEVA COLECCIÓN DE POSTMAN")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Base URL: {BASE_URL}")
    print(f"Username: {USERNAME}")
    
    # Test 1: Login
    print("\n" + "="*60)
    print("TEST 1: LOGIN")
    print("="*60)
    login_success = simulate_login()
    
    if not login_success:
        print("❌ Login falló. Abortando pruebas.")
        return
    
    # Test 2: User Info inmediatamente después del login
    print("\n" + "="*60)
    print("TEST 2: USER INFO (inmediatamente después del login)")
    print("="*60)
    userinfo_success = simulate_user_info()
    
    # Test 3: Refresh Token
    print("\n" + "="*60)
    print("TEST 3: REFRESH TOKEN")
    print("="*60)
    refresh_success = simulate_refresh_token()
    
    # Test 4: User Info con token refrescado
    if refresh_success:
        print("\n" + "="*60)
        print("TEST 4: USER INFO (con token refrescado)")
        print("="*60)
        userinfo_after_refresh = simulate_user_info()
    else:
        userinfo_after_refresh = False
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"✅ Login: {'EXITOSO' if login_success else 'FALLÓ'}")
    print(f"✅ User Info (inicial): {'EXITOSO' if userinfo_success else 'FALLÓ'}")
    print(f"✅ Refresh Token: {'EXITOSO' if refresh_success else 'FALLÓ'}")
    print(f"✅ User Info (post-refresh): {'EXITOSO' if userinfo_after_refresh else 'FALLÓ'}")
    
    all_tests_passed = all([login_success, userinfo_success, refresh_success, userinfo_after_refresh])
    
    if all_tests_passed:
        print("\n🎉 TODAS LAS PRUEBAS PASARON - LA NUEVA COLECCIÓN FUNCIONA CORRECTAMENTE")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON - REVISAR LOGS ARRIBA")
    
    return all_tests_passed

if __name__ == "__main__":
    main()