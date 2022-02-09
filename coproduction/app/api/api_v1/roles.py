from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps
from app.extern import acl

router = APIRouter()


@router.get("", response_model=List[schemas.RoleOut])
def list_roles(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve roles.
    """
    if not crud.role.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    roles = crud.role.get_multi(db, skip=skip, limit=limit)
    return roles


@router.post("", response_model=schemas.RoleOutFull)
def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role_in: schemas.RoleCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new role.
    """
    if not crud.role.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    role = crud.role.create(db=db, role=role_in)
    return role


@router.put("/{id}", response_model=schemas.RoleOutFull)
def update_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    role_in: schemas.RolePatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an role.
    """
    #TODO: check that one member at least is admin
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if not crud.role.can_update(current_user, role):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    role = crud.role.update(db=db, db_obj=role, obj_in=role_in)
    return role


@router.get("/{id}", response_model=schemas.RoleOutFull)
def read_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get role by ID.
    """
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if not crud.role.can_read(db=db, user=current_user, object=role):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return role


@router.delete("/{id}", response_model=schemas.RoleOutFull)
def delete_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an role.
    """
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if not crud.role.can_remove(current_user, role):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.role.remove(db=db, id=id)
    return None
