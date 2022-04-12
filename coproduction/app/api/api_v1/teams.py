import os
from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from app import crud, models, schemas
from app.general import deps
import aiofiles
from slugify import slugify
from fastapi_pagination import Page
from pydantic import BaseModel

from app.messages import log

router = APIRouter()


@router.get("", response_model=Page[schemas.TeamOutFull])
async def list_teams(
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
    coproductionprocess_id: uuid.UUID = Query(None),
) -> Any:
    return await crud.team.get_multi_filtered(db, coproductionprocess_id)

@router.get("/mine", response_model=List[schemas.TeamOutFull])
async def list_my_teams(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve teams.
    """
    return await crud.team.get_multi_by_user(db, user_id=current_user.id)

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

        team = await crud.team.create(db=db, team=team_in, creator=current_user)

        await log({
            "model": "TEAM",
            "action": "CREATE",
            "crud": False,
            "team_id": team.id
        })

        return team

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
        name = slugify(team.name)
        filename, extension = os.path.splitext(file.filename)
        out_file_path = f"/static/teams/{name}{extension}"

        async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        return await crud.team.update(db=db, db_obj=team, obj_in=schemas.TeamPatch(logotype=out_file_path))
    raise HTTPException(status_code=404, detail="Team not found")

class UserIn(BaseModel):
    user_id: str

@router.post("/{id}/add_user", response_model=schemas.TeamOutFull)
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
        if (user := await crud.user.get(db=db, id=user.user_id)):
            return await crud.team.add_user(db=db, team=team, user=user)
        raise HTTPException(status_code=404, detail="User not found")
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

    await log({
        "model": "TEAM",
        "action": "UPDATE",
        "crud": False,
        "team_id": team.id
    })

    team = await crud.team.update(db=db, db_obj=team, obj_in=team_in)

    return team


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

    await log({
        "model": "TEAM",
        "action": "GET",
        "crud": False,
        "team_id": team.id
    })

    return team


@router.delete("/{id}", response_model=schemas.TeamOutFull)
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

    await log({
        "model": "TEAM",
        "action": "DELETE",
        "crud": False,
        "team_id": team.id
    })

    await crud.team.remove(db=db, id=id)

    return None