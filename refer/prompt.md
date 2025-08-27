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