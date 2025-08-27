#!/usr/bin/env python3
"""
Script de verificación para los archivos JSON de Postman renovados
Verifica que la estructura y contenido de los archivos sea correcta
"""

import json
import os
from pathlib import Path

def test_collection_file():
    """Verifica el archivo de colección de Postman"""
    collection_path = Path("Atom_OCR_AI.postman_collection.json")
    
    if not collection_path.exists():
        print("❌ ERROR: Archivo de colección no encontrado")
        return False
    
    try:
        with open(collection_path, 'r', encoding='utf-8') as f:
            collection = json.load(f)
        
        # Verificar estructura básica
        assert "info" in collection, "Falta sección 'info'"
        assert "item" in collection, "Falta sección 'item'"
        
        # Verificar información de la colección
        info = collection["info"]
        assert info["name"] == "Atom OCR AI - API Collection 2025 (Renovada)", "Nombre incorrecto"
        assert "Colección completa renovada" in info["description"], "Descripción incorrecta"
        
        # Verificar que tiene los grupos principales
        groups = [item["name"] for item in collection["item"]]
        expected_groups = ["🔐 Autenticación", "👥 Gestión de Clientes", "🔧 Sistema"]
        
        for group in expected_groups:
            assert group in groups, f"Falta grupo: {group}"
        
        # Verificar endpoints de autenticación
        auth_group = next(item for item in collection["item"] if item["name"] == "🔐 Autenticación")
        auth_endpoints = [endpoint["name"] for endpoint in auth_group["item"]]
        expected_auth = ["Login", "User Info", "Refresh Token", "Register User (Admin Only)", "Logout"]
        
        for endpoint in expected_auth:
            assert endpoint in auth_endpoints, f"Falta endpoint de autenticación: {endpoint}"
        
        print("✅ Archivo de colección verificado correctamente")
        print(f"   - Nombre: {info['name']}")
        print(f"   - Grupos: {len(groups)}")
        print(f"   - Endpoints de autenticación: {len(auth_endpoints)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR verificando colección: {e}")
        return False

def test_environment_file():
    """Verifica el archivo de entorno de Postman"""
    env_path = Path("Atom_OCR_AI.postman_environment.json")
    
    if not env_path.exists():
        print("❌ ERROR: Archivo de entorno no encontrado")
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            environment = json.load(f)
        
        # Verificar estructura básica
        assert "name" in environment, "Falta nombre del entorno"
        assert "values" in environment, "Falta sección 'values'"
        
        # Verificar nombre del entorno
        assert environment["name"] == "Atom OCR AI - Environment 2025 (Renovado)", "Nombre de entorno incorrecto"
        
        # Verificar variables esenciales
        variables = {var["key"]: var for var in environment["values"]}
        essential_vars = [
            "base_url", "username", "password", "access_token", "refresh_token",
            "current_user_id", "current_user_role", "token_expires_at"
        ]
        
        for var in essential_vars:
            assert var in variables, f"Falta variable esencial: {var}"
        
        # Verificar que las variables de seguridad sean tipo 'secret'
        secret_vars = ["password", "access_token", "refresh_token", "test_user_password"]
        for var in secret_vars:
            if var in variables:
                assert variables[var]["type"] == "secret", f"Variable {var} debería ser tipo 'secret'"
        
        # Verificar valores por defecto
        assert variables["base_url"]["value"] == "http://localhost:8000/api/v1", "URL base incorrecta"
        assert variables["username"]["value"] == "admin", "Username por defecto incorrecto"
        assert variables["password"]["value"] == "admin123", "Password por defecto incorrecto"
        
        print("✅ Archivo de entorno verificado correctamente")
        print(f"   - Nombre: {environment['name']}")
        print(f"   - Variables: {len(variables)}")
        print(f"   - Variables de seguridad: {len([v for v in variables.values() if v['type'] == 'secret'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR verificando entorno: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 === VERIFICACIÓN DE ARCHIVOS POSTMAN RENOVADOS === 🔍")
    print(f"Directorio de trabajo: {os.getcwd()}")
    print()
    
    collection_ok = test_collection_file()
    print()
    environment_ok = test_environment_file()
    print()
    
    if collection_ok and environment_ok:
        print("🎉 === VERIFICACIÓN EXITOSA === 🎉")
        print("✅ Ambos archivos JSON están correctamente estructurados")
        print("✅ Listos para importar en Postman")
        print()
        print("📋 INSTRUCCIONES DE USO:")
        print("1. Importa 'Atom_OCR_AI.postman_collection.json' en Postman")
        print("2. Importa 'Atom_OCR_AI.postman_environment.json' en Postman")
        print("3. Selecciona el entorno 'Atom OCR AI - Environment 2025 (Renovado)'")
        print("4. Ejecuta el endpoint 'Login' primero para obtener tokens")
        print("5. Luego puedes usar cualquier otro endpoint")
        return True
    else:
        print("❌ === VERIFICACIÓN FALLIDA === ❌")
        print("Hay problemas con los archivos JSON")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)