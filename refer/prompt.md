# Prompt 1
El objetivo es desarrollar una API básica utilizando FastAPI que permita extraer información de credenciales de identificación. Comenzaremos implementando un sistema de autenticación utilizando SQLite, ya que este es un prototipo inicial que posteriormente evolucionará hacia un producto más estable con un stack tecnológico mejorado.

El sistema de autenticación incluirá:
1. Un módulo de login con usuario y contraseña
2. Implementación de JWT con refresh tokens
3. Los siguientes endpoints funcionales:
   - /login: Recibe usuario y contraseña, devuelve JWT y refresh token
   - /refresh: Recibe refresh token, devuelve nuevo JWT y refresh token
   - /logout: Maneja el cierre de sesión
   - /userinfo: Recibe JWT y devuelve información del usuario

Requisitos técnicos:
- Estructura de código limpia y bien organizada
- Documentación detallada en Swagger
- Configuración de Docker v2 con timezone America/Mexico_City
- Archivo README.md que incluya:
  - Tecnologías utilizadas
  - Instrucciones de uso progresivas
  - Especificaciones técnicas

La implementación debe considerar:
1. Creación de tabla de usuarios compatible con JWT y refresh tokens
2. Endpoints funcionales con seguridad adecuada
3. Documentación exhaustiva
4. Preparación para migración futura a stack más robusto

## Rework
**Fix de configuración de expiración de tokens JWT:**
Durante el desarrollo se identificó un conflicto entre la configuración de `ACCESS_TOKEN_EXPIRE_MINUTES` en `config.py` y las variables de entorno del archivo `.env`. El archivo `.env` sobrescribía la configuración establecida en código, causando que los tokens expiraran instantáneamente a pesar de estar configurados para durar 8 horas (480 minutos).

**Solución implementada:**
- Verificar siempre la coherencia entre `config.py` y `.env`
- Priorizar la configuración del archivo `.env` como fuente única de verdad
- Actualizar `ACCESS_TOKEN_EXPIRE_MINUTES=480` en `.env` para tokens de 8 horas
- Reiniciar el servidor FastAPI después de cambios en variables de entorno
- Implementar scripts de debugging en Postman para identificar problemas de expiración

**Recomendación para futuros desarrollos:**
Siempre verificar que las variables de entorno y la configuración en código estén alineadas, especialmente al modificar configuraciones de seguridad como la duración de tokens JWT.

# Prompt 2

Implementa un endpoint seguro para que únicamente usuarios con rol 'admin' puedan registrar nuevos usuarios. El endpoint debe: 

1. Validar que el solicitante tenga rol 'admin'
2. Recibir y validar los siguientes campos obligatorios:
   - username (cadena única)
   - password (cadena encriptada)
   - email (formato válido)
   - role (solo aceptar 'admin' o 'user')
   - active (booleano)
3. Garantizar que ningún otro tipo de usuario pueda acceder a esta funcionalidad
4. Implementar autenticación y autorización adecuadas
5. Devolver respuestas HTTP apropiadas:
   - 201 Created al éxito
   - 403 Forbidden para no-admins
   - 400 Bad Request para datos inválidos

## Rework

### Fix del endpoint /api/v1/userinfo - Error AttributeError 'is_superuser'

**Fecha**: 26 de agosto de 2025

**Problema identificado**: 
El endpoint `/api/v1/userinfo` generaba un error `AttributeError: 'User' object has no attribute 'is_superuser'` al intentar acceder a un campo que ya no existe en el modelo User.

**Causa raíz**: 
Durante la implementación del sistema de roles (Prompt 1), se reemplazó el campo `is_superuser` por el campo `role` en el modelo User, pero el endpoint `get_user_info` en `app/routers/auth.py` no fue actualizado para usar el nuevo sistema.

**Impacto**: 
El endpoint `/api/v1/userinfo` no funcionaba correctamente, generando errores 500 al intentar obtener información del usuario autenticado.

**Solución implementada**:
1. **Actualización del endpoint**: Modificado `app/routers/auth.py` línea 168
   - Cambio: `is_superuser=current_user.is_superuser` → `role=current_user.role.value`
2. **Verificación del esquema**: Confirmado que `UserResponse` ya estaba correctamente actualizado
3. **Reinicio del servidor**: Aplicación de cambios mediante reinicio de FastAPI

**Archivos modificados**:
- `app/routers/auth.py`: Actualización del endpoint `get_user_info`

**Resultado**: 
El endpoint `/api/v1/userinfo` ahora funciona correctamente y retorna la información del usuario incluyendo su rol (admin/user) en lugar del campo `is_superuser` obsoleto.

**Recomendación para futuros desarrollos**: 
Al realizar cambios en modelos de base de datos, verificar sistemáticamente todos los endpoints que referencien los campos modificados para evitar errores de atributos inexistentes.

# Prompt 3

Implemente la funcionalidad para que tanto usuarios normales como administradores puedan crear clientes, con el objetivo de que los usuarios generen sus propias credenciales de identificación para aplicaciones autenticadas que accederán a recursos futuros. 

Requisitos:
1. Cree una tabla de clientes que:
   - Esté relacionada con el usuario creador mediante una clave foránea
   - Contenga los campos necesarios para credenciales de identificación
2. Permisos de acceso:
   - Usuarios normales pueden:
     - Crear nuevos clientes
     - Ver/consultar únicamente sus propios clientes
   - Administradores pueden:
     - Ver/consultar todos los clientes del sistema
3. La implementación debe ser escalable para soportar recursos adicionales que se agregarán posteriormente.

## Problemas Encontrados y Soluciones

### Error de Validación en Endpoint de Lista de Clientes (Enero 2025)

#### Problema: Esquema ClientListResponse Incorrecto
**Descripción**: El endpoint GET /clients generaba errores de validación de Pydantic debido a que el esquema `ClientListResponse` estaba definido incorrectamente como un esquema individual de cliente en lugar de un esquema que contenga una lista de clientes con metadatos de paginación.

**Error observado**:
```
client_id
  Field required [type=missing, input_value={'clients': [<Client(id=1...'skip': 0, 'limit': 100}, input_type=dict]
```

**Solución implementada**:
1. Creación del esquema `ClientListItem` para elementos individuales
2. Redefinición de `ClientListResponse` con estructura correcta:
   - `clients: List[ClientListItem]` - Lista de clientes
   - `total: int` - Total de registros
   - `skip: int` - Registros omitidos
   - `limit: int` - Límite de registros
3. Actualización de importaciones agregando `List` desde `typing`
4. Reinicio del servidor para aplicar cambios

**Resultado**: El endpoint `/clients` ahora funciona correctamente y retorna la lista de clientes con paginación sin errores de validación.

### Renovación de Archivos Postman (Enero 2025)

#### Problema 1: Sintaxis de PowerShell
**Descripción**: Al intentar reiniciar WSL con el comando `wsl --shutdown && wsl`, PowerShell no reconoció el operador `&&`.
**Error**: `El token '&&' no es un separador de instrucciones válido en esta versión.`
**Solución**: Usar la sintaxis correcta de PowerShell con punto y coma: `wsl --shutdown; wsl`

#### Problema 2: Estructura de Colección Postman
**Descripción**: La colección original tenía una estructura básica sin organización por carpetas y scripts de prueba limitados.
**Solución**: 
- Implementar estructura de carpetas (Autenticación, Gestión de Clientes, Sistema)
- Agregar scripts de pre-solicitud y prueba robustos
- Incluir manejo de tokens JWT automático
- Validación de respuestas y manejo de errores específicos

#### Problema 3: Variables de Entorno Limitadas
**Descripción**: El entorno original solo contenía variables básicas sin soporte para debugging y seguimiento de estado.
**Solución**:
- Agregar variables de seguimiento (`token_expires_at`, `current_user_id`, `current_user_role`)
- Incluir variables de debugging (`debug_mode`, `timeout_ms`)
- Variables específicas para pruebas (`test_username`, `test_client_name`)

#### Problema 4: Archivos Temporales en Control de Versiones
**Descripción**: Archivos `.pyc` y `.db` estaban siendo incluidos en el repositorio.
**Solución**: Actualizar `.gitignore` para excluir estos archivos automáticamente.