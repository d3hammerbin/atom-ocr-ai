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

### Implementación de Sistema de Credenciales de Cliente (Enero 2025)

Se ha implementado un sistema completo de gestión de credenciales de clientes que incluye la generación automática de `client_id` y `client_secret` con las siguientes características:

#### Funcionalidades Implementadas

**1. Generación de Credenciales Seguras**
- **client_id**: Generado automáticamente usando UUID4 con prefijo "client_" para identificación única
- **client_secret**: Generado usando `secrets.token_urlsafe(32)` para máxima seguridad criptográfica
- Ambos campos garantizan unicidad y cumplen estándares de seguridad

**2. Almacenamiento Seguro**
- **Hashing del client_secret**: Implementado usando HMAC-SHA256 con salt único por cliente
- **Verificación segura**: Método `verify_client_secret()` para validación sin exponer el secreto original
- **Separación de responsabilidades**: El secreto hasheado se almacena en BD, el original solo se muestra una vez

**3. Endpoints de API Actualizados**
- **Creación de cliente**: Genera automáticamente ambas credenciales y las retorna en la respuesta
- **Regeneración de secreto**: Endpoint dedicado para generar nuevo `client_secret` manteniendo el `client_id`
- **Respuestas seguras**: Uso de `ClientResponse.from_orm_with_plain_secret()` para manejar secretos temporales

**4. Migración de Base de Datos**
- Agregada columna `client_secret` a la tabla `clients` con tipo TEXT
- Migración de Alembic aplicada correctamente para mantener consistencia de datos
- Campo nullable para compatibilidad con registros existentes

**5. Validaciones y Pruebas**
- **Colección Postman actualizada**: Pruebas automáticas para validar formato y presencia de credenciales
- **Almacenamiento en entorno**: Variables de Postman para reutilizar credenciales en pruebas posteriores
- **Validaciones de formato**: Verificación de longitud y caracteres válidos en ambas credenciales

#### Consideraciones de Seguridad Implementadas

1. **No reversibilidad**: El `client_secret` hasheado no puede ser revertido al valor original
2. **Salt único**: Cada cliente tiene un salt diferente para prevenir ataques de diccionario
3. **Exposición mínima**: El secreto original solo se muestra en la respuesta de creación/regeneración
4. **Validación robusta**: Verificación segura sin necesidad de almacenar el secreto en texto plano

#### Archivos Modificados

- `app/models.py`: Agregado campo `client_secret` y métodos de hashing/verificación
- `app/routers/clients.py`: Actualizada lógica de creación y regeneración de credenciales
- `app/schemas.py`: Agregado método `from_orm_with_plain_secret()` para manejo seguro de respuestas
- `Atom_OCR_AI.postman_collection.json`: Nuevas pruebas para validar credenciales
- `alembic/versions/`: Nueva migración para agregar columna `client_secret`

# Prompt 4

Ahora implementaremos el sistema de enmascaramiento de imágenes. Disponemos de archivos PNG en el directorio "./samples/mask/editables/" que definen los tipos de credenciales:

Tipos de máscaras disponibles:
- Tipo 1: t1_back.png y t1_front.png
- Tipo 2: t2_back.png y t2_front.png  
- Tipo 3: t3_back.png y t3_front.png

En el editor de imágenes (#image-crop-editor.html), agregaremos una barra de herramientas debajo del header con los siguientes controles:
1. Un dropdown para seleccionar el tipo de credencial (1, 2 o 3)
2. Un dropdown para seleccionar el lado (front/delantera o back/trasera)

Al seleccionar estas opciones, se cargará automáticamente el archivo PNG correspondiente como máscara en el canvas. La máscara tiene las siguientes características:
- Tamaño fijo de 709px × 490px (igual que el canvas)
- Color rojo con transparencia para visualizar la imagen subyacente
- Comportamiento estático (no editable)

Nota importante: Los controles de edición deben afectar únicamente a la imagen subyacente, no a la máscara. La máscara sirve únicamente como guía de posicionamiento.

## Problemas Encontrados y Soluciones - Prompt 4

#### Problema 1: Botones de Acción Habilitados Sin Selección de Máscara
**Descripción**: Los botones "Recortar", "Aplicar", "Guardar", "Centrar" y "Restablecer" estaban habilitados desde el inicio, permitiendo acciones sin haber seleccionado tipo y lado de credencial.
**Solución**: 
- Implementación del método `updateActionButtonsState()` que deshabilita los botones hasta que ambos selectores tengan valores
- Integración en constructor, `onMaskControlChange()` y `resetMaskSelectors()`
- Uso de clases CSS `disabled` y atributo `disabled` para control visual y funcional

#### Problema 2: Canvas No Se Limpiaba Al Cargar Nueva Carpeta
**Descripción**: Al seleccionar una nueva carpeta, el canvas mantenía la imagen anterior visible, causando confusión visual.
**Solución**: 
- Modificación del método `loadImagesFromFolder()` para incluir `ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)`
- Reset de variables de imagen (`currentImage`, `originalImage`, `currentImageFile`, `currentImageIndex`)
- Llamada a `resetMaskSelectors()` para limpiar estado de máscaras

#### Problema 3: Indicador Visual de Selección Inconsistente
**Descripción**: 
- El efecto hover interfería con el estado selected
- La imagen seleccionada no mantenía su resaltado visual
- El método `renderImageList()` eliminaba la clase `selected` al regenerar la lista
**Solución**: 
- Modificación de CSS: `.image-item:hover:not(.selected)` para evitar conflictos
- Agregado de `!important` a estilos de `.image-item.selected` para prioridad
- Implementación de lógica en `renderImageList()` para preservar selección actual usando `this.currentImageIndex`

#### Problema 4: Error de Sintaxis JavaScript
**Descripción**: `SyntaxError: Unexpected identifier 'loadMask'` causado por llave de cierre faltante en `onMaskControlChange()`.
**Solución**: Corrección de estructura de llaves en el método, asegurando que `this.drawImage()` esté dentro del bloque correcto.

#### Mejoras Implementadas
1. **Sistema de Control de Estado**: Botones se habilitan/deshabilitan dinámicamente según selección de máscaras
2. **Limpieza Automática**: Canvas y variables se resetean automáticamente al cambiar carpetas
3. **Indicador Visual Mejorado**: Gradiente azul, sombra y desplazamiento para imagen seleccionada
4. **Persistencia de Selección**: La selección visual se mantiene incluso al actualizar la lista de imágenes

# Prompt 5

Hemos completado la investigación para avanzar con la clasificación de credenciales de identificación y sus lados, basándonos en características documentadas previamente. El siguiente paso consiste en implementar un nuevo endpoint para la carga de imágenes con los siguientes requisitos:

1. Funcionalidad de carga:
   - Procesar una imagen por vez
   - Aceptar campos adicionales:
     * Lado de la credencial (back/front)
     * Tipo de documento (1, 2, 3)

2. Procesamiento inicial:
   - Convertir la imagen a escala de grises manteniendo su formato original
   - Almacenar temporalmente en "./entropy/temp/"
   - Generar un nombre único usando UUID conservando la extensión original

3. Almacenamiento de metadatos:
   - Crear tabla "ids_warehouse" con campos:
     * ID autoincremental
     * Relación con usuario (tabla: users)
     * Relación con clientes (tabla: clients)
     * Nombre del archivo (post UUID y conversión)
     * Fechas de creación y actualización
     * Campo booleano para estado (procesado/rechazado)

4. Gestión de datos:
   - Actualizar registros según las acciones aplicadas
   - Implementar soft delete para registros (marcado booleano)

## Problemas Encontrados y Soluciones Implementadas

#### Problema 1: Conflicto de Rutas en FastAPI
**Descripción**: El endpoint `/{client_id}` en el router de clientes estaba capturando la ruta `/images`, interpretando "images" como un `client_id`, causando errores 422 de validación.
**Solución**: 
- Reordenamiento de inclusión de routers en `main.py`, colocando el router de imágenes antes que el de clientes
- Agregado del prefijo `/clients` al router de clientes para evitar conflictos
- Eliminación del prefijo `/clients` de los endpoints individuales en `clients.py`

#### Problema 2: Base de Datos Vacía Después de Migraciones
**Descripción**: Alembic indicaba que las migraciones se habían aplicado correctamente, pero el archivo `atom_ocr.db` tenía 0 bytes y no contenía tablas.
**Solución**: Ejecución manual de `alembic upgrade head` para aplicar correctamente las migraciones y crear las tablas necesarias.

#### Problema 3: Archivos de Cache Python en Control de Versiones
**Descripción**: Archivos `.pyc` y directorios `__pycache__` estaban siendo rastreados por git a pesar de estar en `.gitignore`.
**Solución**: 
- Remoción de archivos de cache del índice de git usando `git rm --cached`
- Verificación de que las reglas en `.gitignore` (`__pycache__/` y `*.py[cod]`) estén correctamente configuradas

#### Problema 4: Validación de Enum en Modelo de Base de Datos
**Descripción**: Error `LookupError` indicando que "front" no es un valor válido para el enum `credentialside`, que solo acepta "FRONT" y "BACK".
**Solución**: Asegurar que los valores del enum se envíen en mayúsculas según la definición del modelo.

#### Mejoras de Configuración Implementadas
1. **Estructura de Rutas Mejorada**: Prefijos claros para evitar conflictos entre diferentes módulos
2. **Gestión de Base de Datos**: Verificación de estado de migraciones y aplicación correcta
3. **Control de Versiones Limpio**: Exclusión apropiada de archivos temporales y de cache
4. **Validación de Datos**: Consistencia en formatos de enum y tipos de datos

# Prompt 6
