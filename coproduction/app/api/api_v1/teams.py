import os
import uuid
from typing import Any, List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("", response_model=List[schemas.TeamOutFull])
async def list_teams(
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
    organization_id: uuid.UUID = Query(None),
) -> Any:
    if organization_id:
        if organization := await crud.organization.get(db=db, id=id):
            return await crud.team.get_multi(db=db, user=current_user, organization=organization)
        raise HTTPException(
                status_code=404, detail="Organization not found") 
    return await crud.team.get_multi(db=db, user=current_user)


@router.post("", response_model=schemas.TeamOutFull)
async def create_team(
    *,
    db: Session = Depends(deps.get_db),
    team_in: schemas.TeamCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new team.
    """
    team = await crud.team.get_by_name(db=db, name=team_in.name)
    if not team:
        if team_in.organization_id and await crud.team.can_create(db=db, organization_id=team_in.organization_id, user=current_user):
            return await crud.team.create(db=db, obj_in=team_in, creator=current_user)
        else:
            raise HTTPException(
                status_code=403, detail="You can not create a team for this organization")

    raise HTTPException(status_code=400, detail="Team already exists")


@router.post("/{id}/logotype", response_model=schemas.TeamOutFull)
async def set_logotype(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
) -> Any:
    """
    Create new team.
    """
    if (team := await crud.team.get(db=db, id=id)):
        filename, extension = os.path.splitext(file.filename)
        out_file_path = f"/static/teams/{team.id}{extension}"

        async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        return await crud.team.update(db=db, db_obj=team, obj_in=schemas.TeamPatch(logotype=out_file_path))
    raise HTTPException(status_code=404, detail="Team not found")


class UserIn(BaseModel):
    user_id: str


@router.post("/{id}/users", response_model=schemas.TeamOutFull)
async def add_user(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    user: UserIn
) -> Any:
    """
    Create new team.
    """
    if (team := await crud.team.get(db=db, id=id)):
        if crud.team.can_update(object=team, user=current_user):
            if (user := await crud.user.get(db=db, id=user.user_id)):
                return await crud.team.add_user(db=db, team=team, user=user)
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=403, detail="You do not have permission")
    raise HTTPException(status_code=404, detail="Team not found")


@router.delete("/{id}/users/{user_id}", response_model=schemas.TeamOutFull)
async def remove_user(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    user_id: str
) -> Any:
    """
    Create new team.
    """
    if (team := await crud.team.get(db=db, id=id)):
        if crud.team.can_update(object=team, user=current_user):
            if (user := await crud.user.get(db=db, id=user_id)):
                return await crud.team.remove_user(db=db, team=team, user=user)
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=403, detail="You do not have permission")
    raise HTTPException(status_code=404, detail="Team not found")


@router.put("/{id}", response_model=schemas.TeamOutFull)
async def update_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: schemas.TeamPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an team.
    """
    team = await crud.team.get(db=db, id=id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not crud.team.can_update(current_user, team):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.team.update(db=db, db_obj=team, obj_in=team_in)


@router.get("/{id}", response_model=schemas.TeamOutFull)
async def read_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get team by ID.
    """
    team = await crud.team.get(db=db, id=id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not crud.team.can_read(current_user, team):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return team


@router.delete("/{id}")
async def delete_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an team.
    """
    team = await crud.team.get(db=db, id=id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not crud.team.can_remove(current_user, team):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.team.remove(db=db, id=id)


@router.post("/{id}/administrators")
async def add_administrator(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    user_in: schemas.UserIn,
) -> Any:
    if (user := await crud.user.get(db=db, id=user_in.user_id)):
        if (team := await crud.team.get(db=db, id=id)):
            if crud.team.can_update(user=current_user, object=team):
                return await crud.team.add_administrator(db=db, db_obj=team, user=user)
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this team")
        raise HTTPException(status_code=404, detail="Team not found")
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{id}/administrators/{user_id}")
async def delete_administrator(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    user_id: str
) -> Any:
    if (user := await crud.user.get(db=db, id=user_id)):
        if (team := await crud.team.get(db=db, id=id)):
            if crud.team.can_update(user=current_user, object=team):
                return await crud.team.remove_administrator(db=db, db_obj=team, user=user)
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this team")
        raise HTTPException(status_code=404, detail="Team not found")
    raise HTTPException(status_code=404, detail="User not found")