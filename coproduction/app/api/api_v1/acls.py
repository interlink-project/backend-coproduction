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
from pydantic import BaseModel

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

@router.post("/{id}/check/{action}/{user_id}")
def check_action(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    action: str,
    user_id: str,
) -> Any:
    """
    Check action for user in acl
    """
    acl = crud.acl.get(db=db, id=id)
    if not acl:
        raise HTTPException(status_code=404, detail="Acl not found")
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.acl.check_action(db=db, user=user, action=action)


class RoleSwitch(BaseModel):
    new_role: uuid.UUID
    old_role: uuid.UUID
    membership_id: uuid.UUID

@router.post("/{id}/switch_membership_role")
def switch_membership_role(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    switch_in: RoleSwitch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Switch roles
    """
    acl = crud.acl.get(db=db, id=id)
    if not acl:
        raise HTTPException(status_code=404, detail="Acl not found")
    
    membership = crud.membership.get(db=db, id=switch_in.membership_id)
    if not membership:
        raise HTTPException(status_code=400, detail="Membership not found")
    
    if acl.coproductionprocess.creator_id == membership.user_id:
        raise HTTPException(status_code=400, detail="Creator role can not be modified")

    new_role = crud.role.get(db=db, id=switch_in.new_role)
    old_role = crud.role.get(db=db, id=switch_in.old_role)
    if not old_role or not new_role:
        raise HTTPException(status_code=400, detail="At least one of the roles does not exist")
    
    # TODO: acl_perm
    if new_role not in acl.roles or old_role not in acl.roles:
        raise HTTPException(status_code=400, detail="At least one of the roles does not belong to the specified ACL")

    if not old_role.id == acl.default_role_id:
        membership.roles.remove(old_role)
    membership.roles.append(new_role)
    db.commit()
    return True
    
