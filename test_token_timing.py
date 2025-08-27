#!/usr/bin/env python3
"""
Script para probar el timing de tokens y simular el comportamiento de Postman
con delays entre requests para identificar problemas de sincronización.
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

def log_with_timestamp(message):
    """Log con timestamp para debugging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_login_userinfo_with_delays():
    """Prueba login seguido de userinfo con diferentes delays"""
    log_with_timestamp("=== INICIANDO PRUEBA DE TIMING ===\n")
    
    # Delays a probar (en segundos)
    delays = [0, 0.1, 0.5, 1.0, 2.0, 5.0]
    
    for delay in delays:
        log_with_timestamp(f"--- Probando con delay de {delay} segundos ---")
        
        # 1. Login
        log_with_timestamp("Realizando login...")
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        try:
            login_response = requests.post(
                f"{BASE_URL}/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            log_with_timestamp(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_json = login_response.json()
                access_token = login_json.get("access_token")
                
                log_with_timestamp(f"Token obtenido: {access_token[:50]}...")
                log_with_timestamp(f"Expires in: {login_json.get('expires_in')} segundos")
                
                # 2. Esperar el delay especificado
                if delay > 0:
                    log_with_timestamp(f"Esperando {delay} segundos...")
                    time.sleep(delay)
                
                # 3. Obtener información del usuario
                log_with_timestamp("Obteniendo información del usuario...")
                
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                userinfo_response = requests.get(
                    f"{BASE_URL}/userinfo",
                    headers=headers
                )
                
                log_with_timestamp(f"UserInfo Status: {userinfo_response.status_code}")
                
                if userinfo_response.status_code == 200:
                    userinfo_json = userinfo_response.json()
                    log_with_timestamp(f"✅ ÉXITO - Usuario: {userinfo_json.get('username')}")
                elif userinfo_response.status_code == 401:
                    log_with_timestamp("❌ FALLO - Token expirado o inválido")
                    log_with_timestamp(f"Response: {userinfo_response.text}")
                else:
                    log_with_timestamp(f"❌ ERROR INESPERADO - Status: {userinfo_response.status_code}")
                    log_with_timestamp(f"Response: {userinfo_response.text}")
            else:
                log_with_timestamp(f"❌ LOGIN FALLÓ - Status: {login_response.status_code}")
                log_with_timestamp(f"Response: {login_response.text}")
                
        except Exception as e:
            log_with_timestamp(f"❌ EXCEPCIÓN: {str(e)}")
        
        log_with_timestamp("")

def test_token_validation_over_time():
    """Prueba la validez del token a lo largo del tiempo"""
    log_with_timestamp("=== PRUEBA DE VALIDEZ DEL TOKEN A LO LARGO DEL TIEMPO ===\n")
    
    # 1. Obtener token
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    login_response = requests.post(
        f"{BASE_URL}/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        log_with_timestamp("❌ No se pudo obtener token inicial")
        return
    
    login_json = login_response.json()
    access_token = login_json.get("access_token")
    expires_in = login_json.get("expires_in")
    
    log_with_timestamp(f"Token obtenido, expira en {expires_in} segundos")
    log_with_timestamp(f"Token: {access_token[:50]}...")
    
    # 2. Probar el token cada 30 segundos durante 5 minutos
    test_intervals = [0, 30, 60, 120, 180, 300]  # segundos
    
    start_time = time.time()
    
    for interval in test_intervals:
        if interval > 0:
            wait_time = interval - (time.time() - start_time)
            if wait_time > 0:
                log_with_timestamp(f"Esperando {wait_time:.1f} segundos más...")
                time.sleep(wait_time)
        
        elapsed = time.time() - start_time
        log_with_timestamp(f"--- Probando token después de {elapsed:.1f} segundos ---")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            userinfo_response = requests.get(
                f"{BASE_URL}/userinfo",
                headers=headers
            )
            
            if userinfo_response.status_code == 200:
                log_with_timestamp("✅ Token aún válido")
            elif userinfo_response.status_code == 401:
                log_with_timestamp("❌ Token expirado")
                log_with_timestamp(f"Response: {userinfo_response.text}")
                break
            else:
                log_with_timestamp(f"❓ Status inesperado: {userinfo_response.status_code}")
                
        except Exception as e:
            log_with_timestamp(f"❌ Error: {str(e)}")
            break

if __name__ == "__main__":
    print("Iniciando pruebas de timing de tokens...\n")
    
    # Prueba 1: Diferentes delays entre login y userinfo
    test_login_userinfo_with_delays()
    
    print("\n" + "="*60 + "\n")
    
    # Prueba 2: Validez del token a lo largo del tiempo
    test_token_validation_over_time()
    
    log_with_timestamp("=== PRUEBAS COMPLETADAS ===")