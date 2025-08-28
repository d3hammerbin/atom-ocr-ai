from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.database import init_db, create_test_user
from app.routers import auth, clients, images
from app.config import settings

# Configuración del contexto de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar base de datos al arrancar
    init_db()
    # Crear usuario de prueba
    create_test_user()
    yield
    # Cleanup al cerrar (si es necesario)

# Crear instancia de FastAPI
app = FastAPI(
    title="Atom OCR AI - API de Autenticación",
    description="API básica para extracción de información de credenciales con autenticación JWT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(images.router, prefix="/api/v1", tags=["Imágenes"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["Clientes"])

# Endpoint de salud
@app.get("/health", tags=["Sistema"])
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "ok", "message": "API funcionando correctamente"}

# Endpoint raíz
@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "Atom OCR AI - API de Autenticación",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )