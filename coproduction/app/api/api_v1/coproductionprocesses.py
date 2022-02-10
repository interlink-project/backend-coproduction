import os
import uuid
from typing import Any, List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from slugify import slugify
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.general import deps

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
    return crud.coproductionprocess.get_multi_by_user(db, user_id=current_user.id)


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
    coproductionprocess = crud.coproductionprocess.create(
        db=db, coproductionprocess=coproductionprocess_in, creator=current_user)
    return coproductionprocess


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


@router.get("/{id}/phases/", response_model=List[schemas.PhaseOut])
def list_related_phases(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve related phases.
    """
    coproductionprocess = crud.coproductionprocess.get(db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=400, detail="CoproductionProcess not found")
    return coproductionprocess.phases


@router.get("/{id}/tree", response_model=List[schemas.PhaseOutFull])
def get_coproductionprocess_tree(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess phases tree.
    """
    coproductionprocess = crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionprocess.phases
