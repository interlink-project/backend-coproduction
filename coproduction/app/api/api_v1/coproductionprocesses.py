import os
import uuid
from typing import Any, List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from slugify import slugify
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("", response_model=List[schemas.CoproductionProcessOut])
async def list_coproductionprocesses(
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
    return await crud.coproductionprocess.get_multi(db, skip=skip, limit=limit)

@router.get("/mine", response_model=List[schemas.CoproductionProcessOut])
async def list_my_coproductionprocesses(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve coproductionprocesses.
    """
    if not crud.coproductionprocess.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.get_multi_by_user(db, user=current_user)


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
    team = None
    if coproductionprocess_in.team_id and not (team := await crud.team.get(db=db, id=coproductionprocess_in.team_id)):
        raise HTTPException(status_code=400, detail="Team does not exist")
    return await crud.coproductionprocess.create(db=db, coproductionprocess=coproductionprocess_in, creator=current_user, team=team)


@router.post("/{id}/logotype", response_model=schemas.CoproductionProcessOutFull)
async def set_logotype(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
        name = slugify(coproductionprocess.name)
        filename, extension = os.path.splitext(file.filename)
        out_file_path = f"/static/coproductionprocesses/{name}{extension}"

        async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        return await crud.coproductionprocess.update(db=db, db_obj=coproductionprocess, obj_in=schemas.CoproductionProcessPatch(logotype=out_file_path))
    raise HTTPException(status_code=404, detail="Coproduction process not found")


@router.post("/{id}/set_schema", response_model=schemas.CoproductionProcessOutFull )
async def set_schema(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    schema: dict,
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
        return await crud.coproductionprocess.set_schema(db=db, coproductionschema=schema, coproductionprocess=coproductionprocess)
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


class UserIn(BaseModel):
    user_id: str

@router.get("/{id}/my_roles")
async def get_my_roles(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get role by ID.
    """
    if process := await crud.coproductionprocess.get(db=db, id=id):
        return await crud.role.get_roles_of_user_for_coproductionprocess(db=db, coproductionprocess=process, user=current_user)
    raise HTTPException(status_code=404, detail="Coproductionprocess not found")


@router.post("/{id}/add_user")
async def add_user(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    user_in: UserIn,
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
    if not crud.coproductionprocess.can_update(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.update(
        db=db, db_obj=coproductionprocess, obj_in=coproductionprocess_in)



@router.get("/{id}", response_model=schemas.CoproductionProcessOutFull)
async def read_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
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


@router.delete("/{id}", response_model=schemas.CoproductionProcessOutFull)
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
    if not crud.coproductionprocess.can_remove(db=db, user=current_user, object=coproductionprocess):
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
