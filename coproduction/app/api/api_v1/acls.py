import ast
import json
import uuid
from typing import Any, List, Optional

import requests
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps
from app.config import settings

router = APIRouter()


@router.post("/roles", response_model=schemas.RoleOut)
def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role: schemas.RoleCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get acl by ID.
    """
    acl = crud.acl.get(db=db, id=role.acl_id)
    if not acl:
        raise HTTPException(status_code=404, detail="Acl not found")
    return crud.role.create(db=db, role=role)


@router.get("/roles/{id}", response_model=schemas.RoleOut)
def get_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get role by ID.
    """
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/roles/{id}", response_model=schemas.RoleOut)
def update_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    role_in: schemas.RolePatch,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Patch role by ID.
    """
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return crud.role.update(db=db, db_obj=role, obj_in=role_in)


@router.delete("/roles/{id}")
def delete_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Delete role by ID.
    """
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if not crud.role.can_remove(current_user, role):
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    return crud.role.remove(db=db, id=role.id)

# ACL

@router.get("/{id}", response_model=schemas.ACLOutFull)
def read_acl(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get acl by ID.
    """
    acl = crud.acl.get(db=db, id=id)
    if not acl:
        raise HTTPException(status_code=404, detail="Acl not found")
    if not crud.acl.can_read(current_user, acl):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return acl

@router.get("/{id}/roles", response_model=List[schemas.RoleOut])
def acl_roles(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get acl by ID.
    """
    acl = crud.acl.get(db=db, id=id)
    if not acl:
        raise HTTPException(status_code=404, detail="Acl not found")
    if not crud.acl.can_read(current_user, acl):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return acl.roles


@router.post("/{id}/switch_membership_role")
def switch_membership_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    switch_in: schemas.RoleSwitch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Switch roles
    """
    acl = crud.acl.get(db=db, id=id)
    if not acl:
        raise HTTPException(status_code=404, detail="Acl not found")
    
    print("llega")
    membership = crud.membership.get(db=db, id=switch_in.membership_id)
    if not membership:
        raise HTTPException(status_code=400, detail="Membership not found")
    
    print("llega 2")
    if acl.coproductionprocess.creator_id == membership.user_id:
        raise HTTPException(status_code=400, detail="Creator role can not be modified")

    
    new_role = crud.role.get(db=db, id=switch_in.new_role)
    old_role = crud.role.get(db=db, id=switch_in.old_role)
    if not old_role or not new_role:
        raise HTTPException(status_code=400, detail="At least one of the roles does not exist")
    
    # TODO: acl_perm
    if new_role in acl.roles and old_role in acl.roles:
        membership.roles.remove(old_role)
        membership.roles.append(new_role)
        db.commit()
        return True
    raise HTTPException(status_code=400, detail="At least one of the roles does not belong to the specified ACL")
