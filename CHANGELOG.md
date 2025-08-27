# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Añadido
- Colección de Postman completamente renovada (Atom_OCR_AI.postman_collection.json)
- Entorno de Postman renovado con variables mejoradas (Atom_OCR_AI.postman_environment.json)
- Estructura organizada por carpetas en colección Postman (Autenticación, Gestión de Clientes, Sistema)
- Scripts de pre-solicitud y prueba avanzados con manejo automático de tokens JWT
- Variables de entorno mejoradas para debugging y seguimiento de estado
- Validación automática de respuestas y manejo de errores específicos en Postman
- Documentación de problemas encontrados y soluciones en prompt.md
- Archivo .gitignore mejorado con exclusiones para archivos Python y base de datos
- Sistema de roles de usuario (admin/user) con enum UserRole
- Endpoint POST /api/v1/register para registro de nuevos usuarios
- Función de autorización require_admin_role para endpoints administrativos
- Validaciones de unicidad para username y email en registro
- Esquema UserCreate con validaciones de contraseña y email
- Documentación Swagger actualizada para nuevo endpoint de registro
- Sistema completo de gestión de clientes para credenciales de identificación
- Modelo Client con relación a User y campos para credenciales (client_id, client_secret)
- Endpoints CRUD para clientes: POST, GET, PUT, DELETE /api/v1/clients
- Endpoint POST /api/v1/clients/{client_id}/regenerate-secret para regenerar secretos
- Autorización diferenciada: usuarios ven solo sus clientes, admins ven todos
- Esquemas Pydantic ClientCreate, ClientResponse, ClientUpdate, ClientListResponse
- Generación automática de client_id y client_secret únicos
- Validaciones de integridad y unicidad para credenciales de clientes

### Cambiado
- Modelo User: reemplazado campo is_superuser por role (UserRole enum)
- Esquema UserResponse: actualizado para usar campo role en lugar de is_superuser
- Endpoint /api/v1/userinfo: corregido para devolver role en lugar de is_superuser
- README.md: actualizada documentación con nuevo endpoint y sistema de roles
- Especificaciones técnicas: actualizada estructura de tabla users
- README.md: añadida documentación completa de endpoints de gestión de clientes
- Especificaciones técnicas: añadida documentación de tabla clients
- Modelo User: añadida relación inversa clients para acceso bidireccional

### Corregido
- AttributeError en endpoint /api/v1/userinfo por referencia a campo obsoleto is_superuser
- Configuración de expiración de tokens JWT en archivo .env
- Problema de tokens que expiraban inmediatamente después del login
- Validación de tokens en endpoints protegidos

### Técnico
- Migración automática de base de datos para cambio de is_superuser a role
- Implementación de decorador de autorización para roles administrativos
- Validaciones de integridad de datos en registro de usuarios
- Mejora en la gestión de configuración JWT para entornos de desarrollo y producción
- Router clients.py registrado en main.py con prefijo /api/v1
- Implementación de lógica de autorización por propietario en endpoints de clientes
- Métodos estáticos para generación segura de credenciales en modelo Client
- Arquitectura escalable preparada para recursos adicionales futuros

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