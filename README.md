# Atom OCR AI - API de Autenticación

API básica desarrollada con FastAPI para extracción de información de credenciales de identificación con sistema de autenticación JWT completo.

## Tecnologías Utilizadas

### Backend
- **FastAPI 0.104.1** - Framework web moderno y rápido para construir APIs
- **SQLAlchemy 2.0.23** - ORM para manejo de base de datos
- **SQLite** - Base de datos ligera para prototipado
- **Uvicorn** - Servidor ASGI de alto rendimiento

### Autenticación y Seguridad
- **JWT (JSON Web Tokens)** - Autenticación basada en tokens
- **Passlib + Bcrypt** - Hash seguro de contraseñas
- **Python-JOSE** - Manejo de tokens JWT
- **Refresh Tokens** - Sistema de renovación de tokens

### Validación y Configuración
- **Pydantic 2.5.0** - Validación de datos y serialización
- **Pydantic Settings** - Manejo de configuración con variables de entorno
- **Email Validator** - Validación de direcciones de correo

### Contenedorización
- **Docker** - Contenedorización de la aplicación
- **Docker Compose** - Orquestación de servicios
- **Timezone**: America/Mexico_City

### Herramientas de Interfaz
- **Image Crop Editor** - Editor web para recorte y procesamiento de imágenes de credenciales
  - Sistema de máscaras predefinidas para diferentes tipos de credenciales
  - Controles de transformación (rotación, escala, posición)
  - Interfaz intuitiva con selección visual de imágenes
  - Validación de estado y controles dinámicos
  - Soporte para múltiples formatos de imagen
- **QR Extractor Pro** - Herramienta especializada para extracción de códigos QR
- **Image Editor** - Editor básico de imágenes con funcionalidades de ajuste

## Estructura del Proyecto

```
atom-ocr-ai/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuración de la aplicación
│   ├── database.py            # Configuración de base de datos
│   ├── models.py              # Modelos SQLAlchemy
│   ├── schemas.py             # Esquemas Pydantic
│   ├── auth_service.py        # Servicio de autenticación
│   └── routers/
│       ├── __init__.py
│       └── auth.py            # Endpoints de autenticación
├── main.py                    # Punto de entrada de la aplicación
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Configuración Docker
├── docker-compose.yml         # Orquestación Docker
├── .dockerignore             # Archivos excluidos del build
├── .env                      # Variables de entorno
└── README.md                 # Documentación
```

## Instalación y Configuración

### Requisitos Previos
- Python 3.11+
- Docker y Docker Compose (opcional)
- Git

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd atom-ocr-ai
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# El archivo .env ya está configurado con valores por defecto
# Modificar SECRET_KEY en producción
```

5. **Ejecutar la aplicación**
```bash
python main.py
```

La API estará disponible en: `http://localhost:8000`

### Instalación con Docker

1. **Construir y ejecutar con Docker Compose**
```bash
docker-compose up --build
```

2. **Ejecutar en segundo plano**
```bash
docker-compose up -d
```

3. **Ver logs**
```bash
docker-compose logs -f
```

4. **Detener servicios**
```bash
docker-compose down
```

## Endpoints de la API

### Autenticación

#### POST `/api/v1/login`
Autentica un usuario y devuelve tokens JWT.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/api/v1/refresh`
Renueva el token de acceso usando un refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### POST `/api/v1/logout`
Cierra la sesión del usuario revocando todos sus refresh tokens.

**Headers:**
```
Authorization: Bearer <access_token>
```

#### GET `/api/v1/userinfo`
Obtiene información del usuario autenticado.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@atomocr.ai",
  "full_name": "Administrador del Sistema",
  "is_active": true,
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-15T15:45:00Z"
}
```

#### POST `/api/v1/register`
Registra un nuevo usuario en el sistema. **Requiere autenticación y rol de administrador.**

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "username": "nuevo_usuario",
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura",
  "full_name": "Nombre Completo",
  "role": "user"
}
```

**Response:**
```json
{
  "id": 2,
  "username": "nuevo_usuario",
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Completo",
  "is_active": true,
  "role": "user",
  "created_at": "2024-01-15T16:30:00Z",
  "last_login": null
}
```

### Gestión de Clientes

#### POST `/api/v1/clients`
Crea un nuevo cliente para generar credenciales de identificación.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Mi Aplicación",
  "description": "Aplicación web para gestión de inventario"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Mi Aplicación",
  "description": "Aplicación web para gestión de inventario",
  "client_id": "app_abc123def456",
  "client_secret": "secret_xyz789uvw012",
  "is_active": true,
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_used": null
}
```

#### GET `/api/v1/clients`
Obtiene la lista de clientes. Los usuarios normales solo ven sus propios clientes, los administradores ven todos.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a devolver (default: 100)

**Response:**
```json
{
  "clients": [
    {
      "id": 1,
      "name": "Mi Aplicación",
      "description": "Aplicación web para gestión de inventario",
      "client_id": "app_abc123def456",
      "is_active": true,
      "user_id": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "last_used": null
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

#### GET `/api/v1/clients/{client_id}`
Obtiene los detalles de un cliente específico.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "name": "Mi Aplicación",
  "description": "Aplicación web para gestión de inventario",
  "client_id": "app_abc123def456",
  "client_secret": "secret_xyz789uvw012",
  "is_active": true,
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_used": null
}
```

#### PUT `/api/v1/clients/{client_id}`
Actualiza la información de un cliente.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Mi Aplicación Actualizada",
  "description": "Nueva descripción",
  "is_active": true
}
```

#### DELETE `/api/v1/clients/{client_id}`
Elimina un cliente del sistema.

**Headers:**
```
Authorization: Bearer <access_token>
```

#### POST `/api/v1/clients/{client_id}/regenerate-secret`
Regenera el client_secret de un cliente.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "client_secret": "secret_new789xyz012",
  "message": "Client secret regenerado exitosamente"
}
```

### Sistema

#### GET `/health`
Verifica el estado de la API.

#### GET `/`
Información básica de la API.

## Usuario de Prueba

La aplicación crea automáticamente un usuario administrador para pruebas:

- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@atomocr.ai`

## Documentación Interactiva

La API incluye documentación interactiva automática:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### 📮 Colección de Postman

Se incluyen archivos de Postman para facilitar las pruebas de la API:

- **Colección**: `Atom_OCR_AI.postman_collection.json`
- **Entorno**: `Atom_OCR_AI.postman_environment.json`

#### Importar en Postman:

1. Abre Postman
2. Haz clic en "Import" en la esquina superior izquierda
3. Arrastra y suelta ambos archivos JSON o selecciónalos manualmente
4. La colección incluye:
   - **Login**: Autenticación con credenciales (guarda tokens automáticamente)
   - **Refresh Token**: Renovación del access token
   - **User Info**: Obtener información del usuario autenticado
   - **Logout**: Cerrar sesión e invalidar tokens
   - **Health Check**: Verificar estado de la API

#### Colección de Postman Renovada (2025)

El proyecto incluye archivos de Postman completamente renovados para facilitar las pruebas de la API:

#### Archivos Incluidos
- `Atom_OCR_AI.postman_collection.json` - Colección renovada con estructura mejorada
- `Atom_OCR_AI.postman_environment.json` - Entorno renovado con variables actualizadas

#### Características de la Colección Renovada
- **Estructura organizada por carpetas:**
  - Autenticación (Login, Register, User Info, Refresh Token, Logout)
  - Gestión de Clientes (Create Client, List Clients)
  - Sistema (Health Check, System Version)

- **Scripts de pre-solicitud y prueba avanzados:**
  - Manejo automático de tokens JWT
  - Validación de respuestas y códigos de estado
  - Manejo de errores específicos (401, 403, 422)
  - Logging detallado para debugging
  - Verificación de expiración de tokens

- **Variables de entorno mejoradas:**
  - Variables de seguimiento (`token_expires_at`, `current_user_id`, `current_user_role`)
  - Variables de debugging (`debug_mode`, `timeout_ms`)
  - Variables específicas para pruebas (`test_username`, `test_client_name`)

#### Instrucciones de Uso
1. Importar ambos archivos JSON en Postman
2. Seleccionar el entorno "Atom OCR AI - Environment 2025 (Renovado)"
3. Ejecutar el endpoint "Login" para obtener tokens
4. Los demás endpoints utilizarán automáticamente los tokens obtenidos
5. Consultar la documentación interactiva en http://localhost:8000/docs

### Variables de Entorno:

- `base_url`: URL base de la API (http://localhost:8000)
- `access_token`: Token JWT (se guarda automáticamente tras login)
- `refresh_token`: Token de renovación (se guarda automáticamente tras login)
- `username`: Usuario de prueba (admin)
- `password`: Contraseña de prueba (admin123)

## Configuración

### Variables de Entorno

Las siguientes variables pueden configurarse en el archivo `.env`:

```env
# Aplicación
APP_NAME="Atom OCR AI"
DEBUG=true

# Base de datos
DATABASE_URL="sqlite:///./atom_ocr_ai.db"

# JWT
SECRET_KEY="your-super-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7

# Seguridad
BCRYPT_ROUNDS=12

# Servidor
HOST="0.0.0.0"
PORT=8000
```

### Configuración de Producción

1. **Cambiar SECRET_KEY** por una clave segura generada aleatoriamente
2. **Configurar DEBUG=false**
3. **Usar base de datos PostgreSQL o MySQL**
4. **Configurar CORS** para dominios específicos
5. **Implementar HTTPS**
6. **Configurar logging** apropiado

## Especificaciones Técnicas

### Base de Datos

#### Tabla `users`
- `id`: Integer (Primary Key)
- `username`: String(50) (Unique)
- `email`: String(100) (Unique)
- `hashed_password`: String(255)
- `full_name`: String(100)
- `is_active`: Boolean
- `role`: Enum('admin', 'user') - Sistema de roles
- `created_at`: DateTime
- `updated_at`: DateTime
- `last_login`: DateTime

#### Tabla `refresh_tokens`
- `id`: Integer (Primary Key)
- `token`: Text (Unique)
- `user_id`: Integer (Foreign Key)
- `expires_at`: DateTime
- `is_revoked`: Boolean
- `created_at`: DateTime

#### Tabla `clients`
- `id`: Integer (Primary Key)
- `name`: String(100) - Nombre del cliente/aplicación
- `description`: Text - Descripción del cliente
- `client_id`: String(50) (Unique) - Identificador único del cliente
- `client_secret`: String(100) - Secreto para autenticación
- `is_active`: Boolean - Estado del cliente
- `user_id`: Integer (Foreign Key) - Usuario propietario
- `created_at`: DateTime
- `updated_at`: DateTime
- `last_used`: DateTime - Última vez que se usó el cliente

### Seguridad

- **Hash de contraseñas:** Bcrypt con 12 rounds
- **Tokens JWT:** HS256 con expiración configurable
- **Refresh tokens:** Almacenados en base de datos con revocación
- **Validación:** Pydantic para todos los inputs
- **CORS:** Configurado para desarrollo (ajustar en producción)

### Rendimiento

- **Servidor ASGI:** Uvicorn con soporte async
- **Base de datos:** SQLAlchemy con pool de conexiones
- **Validación:** Pydantic V2 optimizado
- **Contenedor:** Imagen Python slim optimizada

## Desarrollo

### Comandos Útiles

```bash
# Instalar dependencias de desarrollo
pip install pytest pytest-asyncio httpx

# Ejecutar tests
pytest

# Ejecutar con recarga automática
uvicorn main:app --reload

# Ver logs de Docker
docker-compose logs -f atom-ocr-api
```

### Próximas Mejoras

1. **Migración a stack más robusto**
   - PostgreSQL como base de datos principal
   - Redis para cache y sesiones
   - Nginx como proxy reverso

2. **Funcionalidades adicionales**
   - ✅ Registro de usuarios (implementado)
   - ✅ Sistema de roles básico (implementado)
   - Recuperación de contraseñas
   - Roles y permisos avanzados
   - Rate limiting
   - Logging estructurado

3. **Integración OCR**
   - Endpoints para procesamiento de imágenes
   - Extracción de información de credenciales
   - Almacenamiento de resultados

## Soporte

Para reportar problemas o solicitar funcionalidades, crear un issue en el repositorio del proyecto.

## Licencia

Este proyecto es un prototipo inicial para desarrollo y testing.