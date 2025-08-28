# Estructura del Proyecto Atom OCR AI

## Descripción General

Atom OCR AI es una API REST desarrollada con FastAPI que proporciona servicios de reconocimiento óptico de caracteres (OCR) y clasificación de documentos de identidad. El sistema está diseñado para procesar imágenes de documentos como cédulas, pasaportes y licencias, extrayendo información relevante y almacenándola de forma estructurada.

## Arquitectura del Sistema

### Tecnologías Principales
- **Backend**: FastAPI (Python)
- **Base de Datos**: SQLAlchemy con soporte para múltiples motores
- **Migraciones**: Alembic
- **Autenticación**: Sistema de credenciales con client_id y client_secret
- **Contenedores**: Docker y Docker Compose
- **Testing**: Postman Collections

## Estructura de Directorios

```
atom-ocr-ai/
├── app/                          # Código principal de la aplicación
│   ├── routers/                  # Endpoints de la API
│   │   ├── auth.py              # Autenticación y autorización
│   │   ├── clients.py           # Gestión de clientes
│   │   └── images.py            # Procesamiento de imágenes
│   ├── models.py                # Modelos de base de datos (SQLAlchemy)
│   ├── schemas.py               # Esquemas de validación (Pydantic)
│   ├── database.py              # Configuración de base de datos
│   ├── config.py                # Configuración de la aplicación
│   └── auth_service.py          # Servicios de autenticación
├── alembic/                     # Migraciones de base de datos
│   └── versions/                # Archivos de migración
├── samples/                     # Imágenes de muestra para testing
│   ├── t1/, t2/, t3/           # Tipos de documentos
│   └── mask/                    # Máscaras para procesamiento
├── refer/                       # Documentación y referencias
└── entropy/                     # Directorio para archivos temporales
```

## Componentes Principales

### 1. API Endpoints (`app/routers/`)

#### Autenticación (`auth.py`)
- Manejo de tokens de acceso
- Validación de credenciales de cliente
- Middleware de seguridad

#### Gestión de Clientes (`clients.py`)
- **POST /clients**: Crear nuevo cliente con credenciales únicas
- **GET /clients**: Listar clientes existentes
- **POST /clients/{client_id}/regenerate-secret**: Regenerar client_secret

#### Procesamiento de Imágenes (`images.py`)
- **POST /upload-image**: Subir y procesar imágenes de documentos
- **GET /images**: Listar imágenes procesadas con filtros
- **DELETE /images/{image_id}**: Eliminar imagen específica
- **GET /health**: Verificación de estado del sistema
- **GET /system-info**: Información del sistema

### 2. Modelos de Datos (`models.py`)

#### Tabla `clients`
- `id`: Identificador único
- `client_id`: ID público del cliente
- `client_secret_hash`: Hash seguro del secret
- `salt`: Salt único para hashing
- `created_at`: Fecha de creación
- `is_active`: Estado del cliente

#### Tabla `ids_warehouse`
- `id`: Identificador único
- `client_id`: Referencia al cliente
- `document_type`: Tipo de documento (1=cédula, 2=pasaporte, 3=licencia)
- `credential_side`: Lado del documento (front/back)
- `image_path`: Ruta del archivo de imagen
- `extracted_data`: Datos extraídos en formato JSON
- `created_at`: Fecha de procesamiento

### 3. Esquemas de Validación (`schemas.py`)

#### Enumeraciones
- `DocumentTypeEnum`: Tipos de documento válidos (1, 2, 3)
- `CredentialSideEnum`: Lados del documento (front, back)

#### Esquemas de Request/Response
- `ClientCreate/ClientResponse`: Gestión de clientes
- `ImageUpload/ImageResponse`: Carga y respuesta de imágenes
- `ImageListResponse`: Listado paginado de imágenes

### 4. Sistema de Seguridad

#### Autenticación por Credenciales
- Cada cliente tiene un `client_id` único (UUID4)
- `client_secret` generado aleatoriamente (32 caracteres)
- Almacenamiento seguro con hash SHA-256 y salt único
- Validación mediante comparación de hashes

#### Funciones de Seguridad (`auth_service.py`)
- `generate_client_credentials()`: Genera credenciales únicas
- `hash_client_secret()`: Crea hash seguro con salt
- `verify_client_secret()`: Valida credenciales

### 5. Base de Datos y Migraciones

#### Configuración (`database.py`)
- Soporte para múltiples motores de base de datos
- Pool de conexiones configurado
- Sesiones con manejo automático de transacciones

#### Migraciones Alembic
- `a5712eac2e5a`: Creación inicial de tabla `ids_warehouse`
- `947a78b0ecc1`: Adición de sistema de credenciales a tabla `clients`

### 6. Configuración (`config.py`)

#### Variables de Entorno
- `DATABASE_URL`: Conexión a base de datos
- `SECRET_KEY`: Clave secreta para JWT
- `CORS_ORIGINS`: Orígenes permitidos para CORS
- `UPLOAD_DIR`: Directorio de carga de archivos

### 7. Contenedorización

#### Docker (`Dockerfile`)
- Imagen base Python 3.9
- Instalación de dependencias
- Configuración de usuario no-root
- Exposición del puerto 8000

#### Docker Compose (`docker-compose.yml`)
- Servicio de aplicación FastAPI
- Servicio de base de datos (configurable)
- Volúmenes para persistencia
- Red interna para comunicación

## Testing y Documentación

### Colección Postman
- **Atom_OCR_AI.postman_collection.json**: Pruebas completas de API
- **Atom_OCR_AI.postman_environment.json**: Variables de entorno para testing
- Pruebas automatizadas para todos los endpoints
- Validación de respuestas y manejo de errores

### Documentación
- **README.md**: Guía de instalación y uso
- **CHANGELOG.md**: Historial de cambios
- **POSTMAN_COLLECTION_INSTRUCTIONS.md**: Instrucciones de testing
- **refer/prompt.md**: Documentación técnica detallada

## Flujo de Trabajo Principal

1. **Registro de Cliente**:
   - Cliente solicita credenciales via POST /clients
   - Sistema genera client_id y client_secret únicos
   - Credenciales se almacenan de forma segura

2. **Autenticación**:
   - Cliente envía credenciales en headers de requests
   - Sistema valida mediante comparación de hashes
   - Acceso autorizado a endpoints protegidos

3. **Procesamiento de Imágenes**:
   - Cliente sube imagen via POST /upload-image
   - Sistema procesa y extrae datos del documento
   - Información se almacena en base de datos
   - Respuesta incluye datos extraídos y metadatos

4. **Consulta de Resultados**:
   - Cliente puede listar imágenes procesadas
   - Filtros disponibles por tipo de documento
   - Paginación para grandes volúmenes de datos

## Características de Seguridad

- **Hashing Seguro**: SHA-256 con salt único por cliente
- **Credenciales Únicas**: UUIDs para client_id, strings aleatorios para secrets
- **Validación Robusta**: Esquemas Pydantic para todos los inputs
- **Manejo de Errores**: Respuestas consistentes y logging detallado
- **CORS Configurado**: Control de acceso desde orígenes específicos

## Escalabilidad y Mantenimiento

- **Arquitectura Modular**: Separación clara de responsabilidades
- **Migraciones Versionadas**: Control de cambios en base de datos
- **Configuración Flexible**: Variables de entorno para diferentes ambientes
- **Testing Automatizado**: Cobertura completa con Postman
- **Documentación Actualizada**: Sincronizada con cambios de código

Este proyecto representa una solución robusta y escalable para el procesamiento de documentos de identidad, con énfasis en la seguridad, mantenibilidad y facilidad de uso.