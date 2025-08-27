#!/usr/bin/env python3
"""
Script para simular exactamente el comportamiento de Postman
con manejo de variables de entorno simuladas.
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

# Simular variables de entorno de Postman
postman_environment = {}

def log_with_timestamp(message):
    """Log con timestamp para debugging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def pm_environment_set(key, value):
    """Simular pm.environment.set de Postman"""
    postman_environment[key] = value
    log_with_timestamp(f"Environment variable set: {key} = {value[:50] if isinstance(value, str) and len(value) > 50 else value}...")

def pm_environment_get(key):
    """Simular pm.environment.get de Postman"""
    value = postman_environment.get(key)
    log_with_timestamp(f"Environment variable get: {key} = {'SET' if value else 'NOT SET'}")
    return value

def pm_environment_unset(key):
    """Simular pm.environment.unset de Postman"""
    if key in postman_environment:
        del postman_environment[key]
        log_with_timestamp(f"Environment variable unset: {key}")
    else:
        log_with_timestamp(f"Environment variable unset (not found): {key}")

def simulate_login_request():
    """Simular exactamente el request de Login de Postman"""
    log_with_timestamp("=== SIMULANDO LOGIN REQUEST ===\n")
    
    # Pre-request script simulation
    log_with_timestamp("Ejecutando pre-request script...")
    # (No hay pre-request script en Login)
    
    # Request
    log_with_timestamp("Enviando request de login...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        log_with_timestamp(f"Response Status: {response.status_code}")
        log_with_timestamp(f"Response Time: {response.elapsed.total_seconds() * 1000:.0f}ms")
        
        # Test script simulation (mejorado)
        log_with_timestamp("\nEjecutando test script...")
        
        if response.status_code == 200:
            log_with_timestamp("✅ LOGIN EXITOSO")
            
            response_json = response.json()
            
            # Limpiar tokens anteriores
            pm_environment_unset('access_token')
            pm_environment_unset('refresh_token')
            
            # Guardar tokens en variables de entorno
            pm_environment_set('access_token', response_json['access_token'])
            pm_environment_set('refresh_token', response_json['refresh_token'])
            
            # Log para debugging mejorado
            log_with_timestamp(f"Access Token (primeros 50 chars): {response_json['access_token'][:50]}...")
            log_with_timestamp(f"Refresh Token (primeros 50 chars): {response_json['refresh_token'][:50]}...")
            log_with_timestamp(f"Token Type: {response_json['token_type']}")
            log_with_timestamp(f"Expires In: {response_json['expires_in']} segundos")
            
            # Verificar que los tokens se guardaron correctamente
            saved_access_token = pm_environment_get('access_token')
            saved_refresh_token = pm_environment_get('refresh_token')
            
            log_with_timestamp(f"Token guardado en entorno (verificación): {'SÍ' if saved_access_token else 'NO'}")
            log_with_timestamp(f"Refresh token guardado en entorno (verificación): {'SÍ' if saved_refresh_token else 'NO'}")
            
            # Tests
            assert saved_access_token == response_json['access_token'], "Access token no coincide"
            assert saved_refresh_token == response_json['refresh_token'], "Refresh token no coincide"
            
            log_with_timestamp("✅ Todos los tests pasaron")
            return True
            
        else:
            log_with_timestamp("❌ LOGIN FALLÓ")
            log_with_timestamp(f"Status Code: {response.status_code}")
            log_with_timestamp(f"Response: {response.text}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"❌ EXCEPCIÓN: {str(e)}")
        return False

def simulate_userinfo_request():
    """Simular exactamente el request de User Info de Postman"""
    log_with_timestamp("\n=== SIMULANDO USER INFO REQUEST ===\n")
    
    # Pre-request script simulation (mejorado)
    log_with_timestamp("Ejecutando pre-request script...")
    log_with_timestamp("=== PRE-REQUEST USER INFO ===")
    
    token = pm_environment_get('access_token')
    refresh_token = pm_environment_get('refresh_token')
    base_url = BASE_URL
    
    log_with_timestamp(f"Base URL: {base_url}")
    log_with_timestamp(f"Access Token disponible: {'SÍ' if token else 'NO'}")
    log_with_timestamp(f"Refresh Token disponible: {'SÍ' if refresh_token else 'NO'}")
    
    if token:
        log_with_timestamp(f"Token (primeros 50 chars): {token[:50]}...")
        log_with_timestamp(f"Token (últimos 20 chars): ...{token[-20:]}")
    else:
        log_with_timestamp("⚠️ WARNING: No access token found. Please login first.")
        return False
    
    # Verificar todas las variables de entorno
    log_with_timestamp("Todas las variables de entorno:")
    for key, value in postman_environment.items():
        if 'token' in key:
            log_with_timestamp(f"  {key}: {'SET' if value else 'EMPTY'}")
        else:
            log_with_timestamp(f"  {key}: {value}")
    
    # Request
    log_with_timestamp("\nEnviando request de user info...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/userinfo",
            headers=headers
        )
        
        # Test script simulation (mejorado)
        log_with_timestamp("\nEjecutando test script...")
        log_with_timestamp("=== RESPONSE USER INFO ===")
        log_with_timestamp(f"Status Code: {response.status_code}")
        log_with_timestamp(f"Response Time: {response.elapsed.total_seconds() * 1000:.0f}ms")
        
        # Verificar headers de respuesta
        content_type = response.headers.get('content-type', 'N/A')
        log_with_timestamp(f"Content-Type: {content_type}")
        
        if response.status_code == 401:
            log_with_timestamp("🚫 TOKEN EXPIRADO O INVÁLIDO")
            log_with_timestamp(f"Response Body: {response.text}")
            
            # Verificar qué token se usó
            used_token = pm_environment_get('access_token')
            log_with_timestamp(f"Token usado (primeros 50 chars): {used_token[:50] if used_token else 'NO TOKEN'}...")
            
            log_with_timestamp("💡 SUGERENCIA: Ejecuta el endpoint de Login nuevamente para obtener un token fresco")
            return False
            
        elif response.status_code == 200:
            log_with_timestamp("✅ USER INFO OBTENIDA EXITOSAMENTE")
            
            response_json = response.json()
            log_with_timestamp(f"User info: {json.dumps(response_json, indent=2)}")
            
            # Validar estructura de respuesta
            required_fields = ['id', 'username', 'email', 'role']
            for field in required_fields:
                assert field in response_json, f"Campo requerido '{field}' no encontrado"
            
            log_with_timestamp("✅ Todos los tests pasaron")
            return True
            
        else:
            log_with_timestamp("❌ ERROR INESPERADO")
            log_with_timestamp(f"Status Code: {response.status_code}")
            log_with_timestamp(f"Response Body: {response.text}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"❌ EXCEPCIÓN: {str(e)}")
        return False

def simulate_postman_collection_run():
    """Simular la ejecución completa de la colección de Postman"""
    log_with_timestamp("🚀 INICIANDO SIMULACIÓN COMPLETA DE POSTMAN COLLECTION\n")
    
    # Inicializar variables de entorno base
    pm_environment_set('base_url', BASE_URL)
    pm_environment_set('username', USERNAME)
    pm_environment_set('password', PASSWORD)
    
    # Paso 1: Login
    login_success = simulate_login_request()
    
    if not login_success:
        log_with_timestamp("❌ Login falló, abortando simulación")
        return False
    
    # Pequeña pausa para simular el tiempo entre requests en Postman
    time.sleep(0.5)
    
    # Paso 2: User Info
    userinfo_success = simulate_userinfo_request()
    
    if userinfo_success:
        log_with_timestamp("\n✅ SIMULACIÓN COMPLETA EXITOSA")
        log_with_timestamp("El flujo de Postman funciona correctamente cuando se simula programáticamente")
        return True
    else:
        log_with_timestamp("\n❌ SIMULACIÓN FALLÓ EN USER INFO")
        log_with_timestamp("Hay un problema en el flujo de User Info")
        return False

if __name__ == "__main__":
    print("Iniciando simulación exacta de Postman...\n")
    
    # Ejecutar múltiples veces para verificar consistencia
    for i in range(3):
        log_with_timestamp(f"\n{'='*60}")
        log_with_timestamp(f"EJECUCIÓN #{i+1}")
        log_with_timestamp(f"{'='*60}")
        
        # Limpiar entorno para cada ejecución
        postman_environment.clear()
        
        success = simulate_postman_collection_run()
        
        if not success:
            log_with_timestamp(f"❌ Ejecución #{i+1} falló")
            break
        else:
            log_with_timestamp(f"✅ Ejecución #{i+1} exitosa")
        
        # Pausa entre ejecuciones
        if i < 2:
            time.sleep(2)
    
    log_with_timestamp("\n=== SIMULACIÓN COMPLETA TERMINADA ===")