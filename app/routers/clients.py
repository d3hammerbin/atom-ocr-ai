from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import Client, User, UserRole
from ..schemas import (
    ClientCreate, 
    ClientResponse, 
    ClientUpdate, 
    ClientListResponse,
    ErrorResponse
)
from .auth import get_current_user, get_admin_user

router = APIRouter(
    responses={
        401: {"model": ErrorResponse, "description": "No autorizado"},
        403: {"model": ErrorResponse, "description": "Acceso denegado"},
        404: {"model": ErrorResponse, "description": "Cliente no encontrado"},
        422: {"model": ErrorResponse, "description": "Error de validación"}
    }
)

def require_admin_or_owner(current_user: User, client: Client) -> bool:
    """Verifica si el usuario actual es admin o propietario del cliente"""
    return current_user.role == UserRole.ADMIN or client.user_id == current_user.id

def can_view_all_clients(current_user: User) -> bool:
    """Verifica si el usuario puede ver todos los clientes (solo admins)"""
    return current_user.role == UserRole.ADMIN

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo cliente.
    
    Tanto usuarios normales como administradores pueden crear clientes.
    Los usuarios normales solo pueden crear clientes para sí mismos.
    """
    try:
        # Generar credenciales únicas
        client_id = Client.generate_client_id()
        client_secret = Client.generate_client_secret()
        
        # Verificar unicidad del client_id (aunque es muy improbable que se repita)
        while db.query(Client).filter(Client.client_id == client_id).first():
            client_id = Client.generate_client_id()
        
        # Crear el cliente
        db_client = Client(
            name=client_data.name,
            description=client_data.description,
            client_id=client_id,
            client_secret=Client.hash_client_secret(client_secret),
            user_id=current_user.id
        )
        
        # Almacenar el client_secret sin hashear temporalmente para la respuesta
        db_client._plain_client_secret = client_secret
        
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        
        return ClientResponse.from_orm_with_plain_secret(db_client)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el cliente. Intente nuevamente."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=ClientListResponse)
async def list_clients(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    active_only: bool = Query(True, description="Mostrar solo clientes activos"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Listar clientes.
    
    - Usuarios normales: ven solo sus propios clientes
    - Administradores: ven todos los clientes del sistema
    """
    query = db.query(Client)
    
    # Filtrar por usuario si no es admin
    if not can_view_all_clients(current_user):
        query = query.filter(Client.user_id == current_user.id)
    
    # Filtrar por estado activo si se solicita
    if active_only:
        query = query.filter(Client.is_active == True)
    
    # Contar total de registros
    total = query.count()
    
    # Aplicar paginación
    clients = query.offset(skip).limit(limit).all()
    
    return ClientListResponse(
        clients=clients,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener un cliente específico por ID.
    
    - Usuarios normales: solo pueden ver sus propios clientes
    - Administradores: pueden ver cualquier cliente
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Verificar permisos
    if not require_admin_or_owner(current_user, client):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a este cliente"
        )
    
    return client

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Actualizar un cliente existente.
    
    - Usuarios normales: solo pueden actualizar sus propios clientes
    - Administradores: pueden actualizar cualquier cliente
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Verificar permisos
    if not require_admin_or_owner(current_user, client):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para modificar este cliente"
        )
    
    try:
        # Actualizar solo los campos proporcionados
        update_data = client_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(client, field, value)
        
        client.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(client)
        
        return ClientResponse.from_orm_with_plain_secret(client)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el cliente"
        )

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Eliminar un cliente.
    
    - Usuarios normales: solo pueden eliminar sus propios clientes
    - Administradores: pueden eliminar cualquier cliente
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Verificar permisos
    if not require_admin_or_owner(current_user, client):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar este cliente"
        )
    
    try:
        db.delete(client)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el cliente"
        )

@router.post("/{client_id}/regenerate-secret", response_model=ClientResponse)
async def regenerate_client_secret(
    client_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Regenerar el client_secret de un cliente.
    
    - Usuarios normales: solo pueden regenerar el secret de sus propios clientes
    - Administradores: pueden regenerar el secret de cualquier cliente
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Verificar permisos
    if not require_admin_or_owner(current_user, client):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para regenerar el secret de este cliente"
        )
    
    try:
        # Generar nuevo client_secret
        new_client_secret = Client.generate_client_secret()
        client.client_secret = Client.hash_client_secret(new_client_secret)
        client.updated_at = datetime.utcnow()
        
        # Almacenar el client_secret sin hashear temporalmente para la respuesta
        client._plain_client_secret = new_client_secret
        
        db.commit()
        db.refresh(client)
        
        return client
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al regenerar el client secret"
        )