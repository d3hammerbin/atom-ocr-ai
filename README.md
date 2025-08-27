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
  "is_superuser": true,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-15T15:45:00Z"
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

#### Variables de Entorno:

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
- `is_superuser`: Boolean
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
   - Registro de usuarios
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