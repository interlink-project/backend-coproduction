import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

from app.messages import log

router = APIRouter()
    
@router.post("", response_model=schemas.PermissionOut)
async def create_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_in: schemas.PermissionCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create permission
    """
    treeitem : models.TreeItem
    if treeitem := await crud.treeitem.get(db=db, id=permission_in.treeitem_id):
        return await crud.permission.create(db=db, obj_in=permission_in, creator=current_user, extra={
            "coproductionprocess_id": treeitem.coproductionprocess_id
        })
    raise HTTPException(status_code=404, detail="treeitem not found")

@router.get("", response_model=List[schemas.PermissionOutFull])
async def get_permissions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get permissions.
    """
    return None

@router.get("/{id}", response_model=schemas.PermissionOutFull)
async def get_permission(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get permission by ID.
    """
    if permission := await crud.permission.get(db=db, id=id):
        return permission
    raise HTTPException(status_code=404, detail="Permission not found")

@router.put("/{id}", response_model=schemas.PermissionOutFull)
async def update_permission(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    permission_in: schemas.PermissionPatch,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Patch permission by ID.
    """
    if permission := await crud.permission.get(db=db, id=id):
        return await crud.permission.update(db=db, db_obj=permission, obj_in=permission_in)
    raise HTTPException(status_code=404, detail="Permission not found")


@router.delete("/{id}")
async def delete_permission(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete permission by ID.
    """
    if permission := await crud.permission.get(db=db, id=id):
        return await crud.permission.remove(db=db, id=permission.id)

    raise HTTPException(status_code=404, detail="Permission not found")



@router.get("/for/{treeitem_id}", response_model=dict)
async def yours(
    *,
    db: Session = Depends(deps.get_db),
    treeitem_id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get permission by ID.
    """
    if treeitem := await crud.treeitem.get(db=db, id=treeitem_id):
        return {
            "your_permissions": crud.permission.get_dict_over_treeitem(db=db, treeitem=treeitem, user=current_user),
            "your_roles": crud.permission.get_user_roles(db=db, treeitem=treeitem, user=current_user)
        }