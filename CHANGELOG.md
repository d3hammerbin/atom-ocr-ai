# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Corregido
- Configuración de expiración de tokens JWT en archivo .env
- Problema de tokens que expiraban inmediatamente después del login
- Validación de tokens en endpoints protegidos (/api/v1/userinfo, /api/v1/verify-token)

### Cambiado
- Duración de ACCESS_TOKEN_EXPIRE_MINUTES aumentada de 30 a 480 minutos (8 horas) para facilitar pruebas
- Configuración JWT documentada en README.md con recomendaciones de seguridad

### Añadido
- Scripts de depuración en colección Postman para endpoints de autenticación
- Logging detallado en scripts de prueba para identificación de problemas
- Validaciones de presencia de tokens en requests de Postman
- Tests automatizados en Postman para verificar guardado correcto de tokens

### Técnico
- Identificación de conflicto entre configuración en config.py y variables de entorno
- Priorización correcta de variables de entorno sobre valores por defecto en código
- Mejora en la gestión de configuración JWT para entornos de desarrollo y producción

## [1.0.0] - 2025-01-27

### Añadido
- Estructura base del proyecto FastAPI con arquitectura modular
- Sistema de autenticación JWT con refresh tokens
- Modelos de base de datos SQLite para usuarios y tokens
- Endpoints de autenticación completos (/login, /refresh, /logout, /userinfo, /verify-token)
- Documentación Swagger automática
- Configuración Docker con timezone America/Mexico_City
- Colección y entorno de Postman para pruebas
- Archivo requirements.txt con dependencias del proyecto
- README.md con documentación técnica completa
- Configuración de variables de entorno (.env)
- Middleware CORS para desarrollo frontend
- Validación de esquemas con Pydantic
- Manejo de errores HTTP estandarizado