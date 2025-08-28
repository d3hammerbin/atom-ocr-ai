from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from PIL import Image
import io
from datetime import datetime

from ..database import get_db
from ..models import IdsWarehouse, User, Client
from ..schemas import (
    ImageUploadResponse, 
    IdsWarehouseListResponse, 
    IdsWarehouseListItem,
    CredentialSideEnum,
    DocumentTypeEnum
)
from .auth import get_current_user

router = APIRouter()

# Directorio para almacenamiento temporal
TEMP_DIR = "./entropy/temp/"

# Extensiones de imagen permitidas
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def validate_image_file(file: UploadFile) -> str:
    """Valida que el archivo sea una imagen válida y retorna la extensión"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
    
    # Obtener extensión del archivo
    file_extension = os.path.splitext(file.filename.lower())[1]
    
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Formato de archivo no soportado. Formatos permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validar que el contenido sea realmente una imagen
    try:
        file.file.seek(0)
        image = Image.open(file.file)
        image.verify()  # Verifica que sea una imagen válida
        file.file.seek(0)  # Resetear posición del archivo
    except Exception:
        raise HTTPException(status_code=400, detail="El archivo no es una imagen válida")
    
    return file_extension


def process_image_to_grayscale(file: UploadFile, output_path: str) -> None:
    """Convierte la imagen a escala de grises y la guarda"""
    try:
        # Leer la imagen
        file.file.seek(0)
        image = Image.open(file.file)
        
        # Convertir a escala de grises
        grayscale_image = image.convert('L')
        
        # Guardar la imagen procesada
        grayscale_image.save(output_path, optimize=True, quality=95)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la imagen: {str(e)}")


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(..., description="Archivo de imagen a procesar"),
    credential_side: str = Form(..., description="Lado de la credencial (front/back)"),
    document_type: DocumentTypeEnum = Form(..., description="Tipo de documento (1, 2, 3)"),
    client_id: int = Form(..., description="ID del cliente asociado"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint para cargar y procesar imágenes de credenciales"""
    
    # Convertir credential_side a mayúsculas para coincidir con el enum de la base de datos
    credential_side_upper = credential_side.upper()
    
    # Validar que el valor sea válido
    if credential_side_upper not in ['FRONT', 'BACK']:
        raise HTTPException(
            status_code=400, 
            detail="Valor inválido para credential_side. Valores permitidos: 'front', 'back' (se aceptan en mayúsculas o minúsculas)"
        )
    
    # Crear el enum para Pydantic (en minúsculas)
    credential_side_enum = CredentialSideEnum(credential_side_upper.lower())
    
    # Validar que el cliente existe y pertenece al usuario (o el usuario es admin)
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar permisos: el cliente debe pertenecer al usuario o el usuario debe ser admin
    if client.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para usar este cliente")
    
    # Validar archivo de imagen
    file_extension = validate_image_file(file)
    
    # Generar nombre único para el archivo
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    output_path = os.path.join(TEMP_DIR, unique_filename)
    
    # Asegurar que el directorio existe
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Procesar imagen a escala de grises
    process_image_to_grayscale(file, output_path)
    
    # Crear registro en base de datos
    db_image = IdsWarehouse(
        user_id=current_user.id,
        client_id=client_id,
        filename=unique_filename,
        original_filename=file.filename,
        credential_side=credential_side_upper,
        document_type=document_type.value,
        is_processed=False,
        is_rejected=False,
        is_deleted=False
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return ImageUploadResponse(
        id=db_image.id,
        filename=db_image.filename,
        original_filename=db_image.original_filename,
        credential_side=db_image.credential_side,
        document_type=db_image.document_type,
        client_id=db_image.client_id,
        user_id=db_image.user_id,
        is_processed=db_image.is_processed,
        created_at=db_image.created_at
    )


@router.get("/images", response_model=IdsWarehouseListResponse)
async def list_images(
    skip: int = 0,
    limit: int = 100,
    client_id: int = None,
    credential_side: str = None,
    document_type: int = None,
    is_processed: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint para listar imágenes almacenadas con filtros opcionales"""
    
    # Construir query base
    query = db.query(IdsWarehouse).filter(IdsWarehouse.is_deleted == False)
    
    # Filtrar por usuario (admins pueden ver todas, usuarios solo las suyas)
    if current_user.role.value != "admin":
        query = query.filter(IdsWarehouse.user_id == current_user.id)
    
    # Aplicar filtros opcionales
    if client_id is not None:
        query = query.filter(IdsWarehouse.client_id == client_id)
    
    if credential_side is not None:
        query = query.filter(IdsWarehouse.credential_side == credential_side)
    
    if document_type is not None:
        query = query.filter(IdsWarehouse.document_type == document_type)
    
    if is_processed is not None:
        query = query.filter(IdsWarehouse.is_processed == is_processed)
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación y ordenar por fecha de creación (más recientes primero)
    images = query.order_by(IdsWarehouse.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convertir a esquemas de respuesta
    image_items = [
        IdsWarehouseListItem(
            id=img.id,
            filename=img.filename,
            original_filename=img.original_filename,
            credential_side=img.credential_side,
            document_type=img.document_type,
            is_processed=img.is_processed,
            is_rejected=img.is_rejected,
            created_at=img.created_at,
            processed_at=img.processed_at
        )
        for img in images
    ]
    
    return IdsWarehouseListResponse(
        images=image_items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.delete("/images/{image_id}")
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint para eliminar (soft delete) una imagen"""
    
    # Buscar la imagen
    image = db.query(IdsWarehouse).filter(
        IdsWarehouse.id == image_id,
        IdsWarehouse.is_deleted == False
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    # Verificar permisos: la imagen debe pertenecer al usuario o el usuario debe ser admin
    if image.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar esta imagen")
    
    # Soft delete
    image.is_deleted = True
    image.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Imagen eliminada exitosamente"}


@router.patch("/images/{image_id}/process")
async def mark_image_as_processed(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint para marcar una imagen como procesada"""
    
    # Buscar la imagen
    image = db.query(IdsWarehouse).filter(
        IdsWarehouse.id == image_id,
        IdsWarehouse.is_deleted == False
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    # Verificar permisos: la imagen debe pertenecer al usuario o el usuario debe ser admin
    if image.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar esta imagen")
    
    # Marcar como procesada
    image.is_processed = True
    image.processed_at = datetime.utcnow()
    image.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Imagen marcada como procesada exitosamente"}


@router.patch("/images/{image_id}/reject")
async def mark_image_as_rejected(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint para marcar una imagen como rechazada"""
    
    # Buscar la imagen
    image = db.query(IdsWarehouse).filter(
        IdsWarehouse.id == image_id,
        IdsWarehouse.is_deleted == False
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    # Verificar permisos: la imagen debe pertenecer al usuario o el usuario debe ser admin
    if image.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar esta imagen")
    
    # Marcar como rechazada
    image.is_rejected = True
    image.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Imagen marcada como rechazada exitosamente"}