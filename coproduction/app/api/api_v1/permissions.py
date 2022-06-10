import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

from app.messages import log

router = APIRouter()

class PermissionSwitch(BaseModel):
    new_permission: uuid.UUID
    old_permission: uuid.UUID
    team_id: Optional[uuid.UUID]
    user_id: Optional[str]

@router.post("/switch")
async def switch_permission(
    *,
    db: Session = Depends(deps.get_db),
    switch_in: PermissionSwitch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Switch permissions
    """
    user = None
    team = None
    if switch_in.user_id and not (user := await crud.user.get(db=db, id=switch_in.user_id)):
        raise HTTPException(status_code=400, detail="User does not exist")

    if switch_in.team_id and not (team := await crud.team.get(db=db, id=switch_in.team_id)):
        raise HTTPException(status_code=400, detail="Team does not exist")

    if not user and not team:
        raise HTTPException(status_code=400, detail="Please, specify a team or a user")
    if user and team:
        raise HTTPException(status_code=400, detail="Please, specify only a team or a user")

    new_permission = await crud.permission.get(db=db, id=switch_in.new_permission)
    old_permission = await crud.permission.get(db=db, id=switch_in.old_permission)
    if not old_permission or not new_permission:
        raise HTTPException(status_code=400, detail="At least one of the permissions does not exist")
    
    if new_permission.treeitem_id != old_permission.treeitem_id:
        raise HTTPException(status_code=400, detail="Creators permission can not be modified")
    if old_permission.treeitem.creator_id == switch_in.user_id:
        raise HTTPException(status_code=400, detail="Permission of the creator can not be modified")

    if user:
        old_permission.users.remove(user)
        new_permission.users.append(user)
    if team:
        old_permission.teams.remove(team)
        new_permission.teams.append(team)
    
    db.commit()
    return True
    
@router.post("", response_model=schemas.PermissionOut)
async def create_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission: schemas.PermissionCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Create permission
    """
    return await crud.permission.create(db=db, obj_in=permission)

@router.get("", response_model=List[schemas.PermissionOutFull])
async def get_permissions(
    *,
    db: Session = Depends(deps.get_db),
    treeitem_id: uuid.UUID = Query(None),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get permission by ID.
    """
    if process := await crud.treeitem.get(db=db, id=treeitem_id):
        return process.permissions
    raise HTTPException(status_code=404, detail="treeitem not found")

@router.get("/{id}", response_model=schemas.PermissionOutFull)
async def get_permission(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
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
    current_user: Optional[models.User] = Depends(deps.get_current_user),
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
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Delete permission by ID.
    """
    if permission := await crud.permission.get(db=db, id=id):
        return await crud.permission.remove(db=db, id=permission.id)

    raise HTTPException(status_code=404, detail="Permission not found")
 
class TeamIn(BaseModel):
    team_id: uuid.UUID

@router.post("/{id}/add_team")
async def add_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: TeamIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add team to permission
    """
    if permission := await crud.permission.get(db=db, id=id):
        if team := await crud.team.get(db=db, id=team_in.team_id):
            await crud.permission.add_team(db=db, permission=permission, team=team)
            return True
        raise HTTPException(status_code=400, detail="Team not found")

    raise HTTPException(status_code=404, detail="Permission not found")


@router.post("/{id}/remove_team")
async def remove_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: TeamIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add team to permission
    """
    if permission := await crud.permission.get(db=db, id=id):
        if team := await crud.team.get(db=db, id=team_in.team_id):
            await crud.permission.remove_team(db=db, permission=permission, team=team)
            return True
        raise HTTPException(status_code=400, detail="Team not found")

    raise HTTPException(status_code=404, detail="Permission not found")
    
    
class UserIn(BaseModel):
    user_id: str

@router.post("/{id}/remove_user")
async def remove_user(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    user_in: UserIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add user to permission
    """
    if permission := await crud.permission.get(db=db, id=id):
        if user := await crud.user.get(db=db, id=user_in.user_id):
            await crud.permission.remove_user(db=db, permission=permission, user=user)
            return True
        raise HTTPException(status_code=400, detail="User not found")

    raise HTTPException(status_code=404, detail="Permission not found")