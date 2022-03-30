import os
import uuid
from typing import Any, List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from slugify import slugify
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.general import deps
from pydantic import BaseModel

router = APIRouter()


@router.get("", response_model=List[schemas.CoproductionProcessOut])
def list_coproductionprocesses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve coproductionprocesses.
    """
    if not crud.coproductionprocess.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    coproductionprocesses = crud.coproductionprocess.get_multi(
        db, skip=skip, limit=limit)
    return coproductionprocesses


@router.get("/mine", response_model=List[schemas.CoproductionProcessOut])
def list_my_coproductionprocesses(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve coproductionprocesses.
    """
    if not crud.coproductionprocess.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.coproductionprocess.get_multi_by_user(db, user=current_user)


@router.post("", response_model=schemas.CoproductionProcessOutFull)
def create_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    coproductionprocess_in: schemas.CoproductionProcessCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new coproductionprocess.
    """
    if not crud.coproductionprocess.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if team := crud.team.get(db=db, id=coproductionprocess_in.team_id):
        coproductionprocess = crud.coproductionprocess.create(
            db=db, coproductionprocess=coproductionprocess_in, creator=current_user, team=team)
        return coproductionprocess
    raise HTTPException(status_code=400, detail="Team does not exist")

@router.post("/{id}/logotype", response_model=schemas.CoproductionProcessOutFull)
async def set_logotype(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user),
    file: UploadFile = File(...),
) -> Any:
    if (coproductionprocess := crud.coproductionprocess.get(db=db, id=id)):
        name = slugify(coproductionprocess.name)
        filename, extension = os.path.splitext(file.filename)
        out_file_path = f"/static/coproductionprocesses/{name}{extension}"

        async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        return crud.team.update(db=db, db_obj=coproductionprocess, obj_in=schemas.CoproductionProcessPatch(logotype=out_file_path))
    raise HTTPException(status_code=404, detail="Coproduction process not found")


class CoproductionSchemaSetter(BaseModel):
    coproductionschema_id: uuid.UUID

@router.post("/{id}/set_schema", response_model=schemas.CoproductionProcessOutFull)
async def set_schema(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    schema_setter: CoproductionSchemaSetter,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    if (coproductionprocess := crud.coproductionprocess.get(db=db, id=id)):
        if (coproductionschema := crud.coproductionschema.get(db=db, id=schema_setter.coproductionschema_id)):
            return crud.coproductionprocess.set_schema(db=db, coproductionschema=coproductionschema, coproductionprocess=coproductionprocess)
        raise HTTPException(status_code=404, detail="Coproduction schema not found")
    raise HTTPException(status_code=404, detail="Coproduction process not found")

class TeamIn(BaseModel):
    team_id: uuid.UUID


@router.post("/{id}/add_team")
def add_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: TeamIn,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add team to coproductionprocess (with default role)
    """
    if coproductionprocess := crud.coproductionprocess.get(db=db, id=id):
        if team := crud.team.get(db=db, id=team_in.team_id):
            return crud.coproductionprocess.add_team(db=db, coproductionprocess=coproductionprocess, team=team)
        raise HTTPException(status_code=400, detail="Team not found")
    raise HTTPException(status_code=404, detail="Coproductionprocess not found")
    

@router.put("/{id}", response_model=schemas.CoproductionProcessOutFull)
def update_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    coproductionprocess_in: schemas.CoproductionProcessPatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an coproductionprocess.
    """
    coproductionprocess = crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_update(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    coproductionprocess = crud.coproductionprocess.update(
        db=db, db_obj=coproductionprocess, obj_in=coproductionprocess_in)
    return coproductionprocess


@router.get("/{id}", response_model=schemas.CoproductionProcessOutFull)
def read_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get coproductionprocess by ID.
    """
    coproductionprocess = crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionprocess


@router.delete("/{id}", response_model=schemas.CoproductionProcessOutFull)
def delete_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an coproductionprocess.
    """
    coproductionprocess = crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_remove(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.coproductionprocess.remove(db=db, id=id)
    return None


# specific

@router.get("/{id}/tree", response_model=Optional[List[schemas.PhaseOutFull]])
def get_coproductionprocess_coproductionschema(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess tree.
    """
    coproductionprocess = crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionprocess.phases

