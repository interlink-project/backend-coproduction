from locale import strcoll
import os
import uuid
from typing import Any, Dict, List, Optional

import aiofiles
import requests
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps
from app.sockets import socket_manager 

router = APIRouter()


@router.get("", response_model=List[schemas.CoproductionProcessOutFull])
async def list_coproductionprocesses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
    search: str = Query(None)
) -> Any:
    """
    Retrieve coproductionprocesses.
    """
    if not crud.coproductionprocess.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.get_multi_by_user(db, user=current_user, search=search)


@router.post("", response_model=schemas.CoproductionProcessOutFull)
async def create_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    coproductionprocess_in: schemas.CoproductionProcessCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new coproductionprocess.
    """
    if not crud.coproductionprocess.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.create(db=db, obj_in=coproductionprocess_in, creator=current_user, set_creator_admin=True)


@router.post("/{id}/logotype", response_model=schemas.CoproductionProcessOutFull)
async def set_logotype(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...),
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
        if crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
            filename, extension = os.path.splitext(file.filename)
            out_file_path = f"/static/coproductionprocesses/{coproductionprocess.id}{extension}"

            async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
                content = await file.read()  # async read
                await out_file.write(content)  # async write
            return await crud.coproductionprocess.update(db=db, db_obj=coproductionprocess, obj_in=schemas.CoproductionProcessPatch(logotype=out_file_path))
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this coproductionprocess")
    raise HTTPException(status_code=404, detail="Coproduction process not found")


@router.post("/{id}/set_schema", response_model=schemas.CoproductionProcessOutFull)
async def set_schema(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    schema: dict,
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
        if crud.coproductionprocess.can_update(current_user, coproductionprocess):
            return await crud.coproductionprocess.set_schema(db=db, coproductionschema=schema, coproductionprocess=coproductionprocess)
        raise HTTPException(
            status_code=404, detail="You do not have permissions to update the coproductionprocess")
    raise HTTPException(status_code=404, detail="Coproduction process not found")


@router.post("/{id}/clear_schema", response_model=schemas.CoproductionProcessOutFull)
async def clear_schema(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
        if crud.coproductionprocess.can_update(current_user, coproductionprocess):
            return await crud.coproductionprocess.clear_schema(db=db, coproductionprocess=coproductionprocess)
        raise HTTPException(
            status_code=404, detail="You do not have permissions to update the coproductionprocess")
    raise HTTPException(status_code=404, detail="Coproduction process not found")



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
    Add team to coproductionprocess (with async default role)
    """
    if coproductionprocess := await crud.coproductionprocess.get(db=db, id=id):
        if team := await crud.team.get(db=db, id=team_in.team_id):
            await crud.coproductionprocess.add_team(
                db=db, coproductionprocess=coproductionprocess, team=team)
            return True
        raise HTTPException(status_code=400, detail="Team not found")
    raise HTTPException(status_code=404, detail="Coproductionprocess not found")

@router.post("/{id}/add_user")
async def add_user(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    user_in: schemas.UserIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add user to coproductionprocess (with async default role)
    """
    if coproductionprocess := await crud.coproductionprocess.get(db=db, id=id):
        if user := await crud.user.get(db=db, id=user_in.user_id):
            await crud.coproductionprocess.add_user(
                db=db, coproductionprocess=coproductionprocess, user=user)
            return True
        raise HTTPException(status_code=400, detail="User not found")
    raise HTTPException(status_code=404, detail="Coproductionprocess not found")


@router.put("/{id}", response_model=schemas.CoproductionProcessOutFull)
async def update_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    coproductionprocess_in: schemas.CoproductionProcessPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an coproductionprocess.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.update(
        db=db, db_obj=coproductionprocess, obj_in=coproductionprocess_in)


@router.get("/{id}", response_model=schemas.CoproductionProcessOutFull)
async def read_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess by ID.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionprocess


@router.delete("/{id}")
async def delete_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an coproductionprocess.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_remove(user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await crud.coproductionprocess.remove(db=db, id=id)
    return None


# specific

@router.get("/{id}/tree", response_model=Optional[List[schemas.PhaseOutFull]])
async def get_coproductionprocess_tree(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess tree.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionprocess.children


# specific

@router.get("/{id}/activity")
async def get_activity(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess activity.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    return requests.get(f"http://logging/api/v1/log?coproductionprocess_ids={id}&size=20").json()


@router.get("/{id}/assets", response_model=List[schemas.AssetOut])
async def read_coproductionprocess_assets(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess by ID.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.get_assets(db=db, user=current_user, coproductionprocess=coproductionprocess)


@router.post("/{id}/administrators")
async def add_administrator(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_in: schemas.UserIn,
) -> Any:
    if (user := await crud.user.get(db=db, id=user_in.user_id)):
        if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
            if crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
                return await crud.coproductionprocess.add_administrator(db=db, db_obj=coproductionprocess, user=user)
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this coproductionprocess")
        raise HTTPException(status_code=404, detail="Coproductionprocess not found")
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{id}/administrators/{user_id}")
async def delete_administrator(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_id: str
) -> Any:
    if (user := await crud.user.get(db=db, id=user_id)):
        if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
            if crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
                return await crud.coproductionprocess.remove_administrator(db=db, db_obj=coproductionprocess, user=user)
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this coproductionprocess")
        raise HTTPException(status_code=404, detail="Coproductionprocess not found")
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/send_message")
async def send_message(
    *,
    id: uuid.UUID,
    message: str
) -> Any:
    await socket_manager.send_to_id(id=id, data={"data": message})


@router.websocket("/{id}/ws")
async def websocket_endpoint(
    *,
    id: uuid.UUID,
    websocket: WebSocket
):
    await socket_manager.connect(websocket, id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        socket_manager.disconnect(websocket, id)
