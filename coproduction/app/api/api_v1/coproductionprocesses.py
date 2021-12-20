from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.CoproductionProcessOut])
def list_coproductionprocesses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve coproductionprocesses.
    """
    if not crud.coproductionprocess.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    coproductionprocesses = crud.coproductionprocess.get_multi(db, skip=skip, limit=limit)
    return coproductionprocesses


@router.post("/", response_model=schemas.CoproductionProcessOutFull)
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
    coproductionprocess = crud.coproductionprocess.create(db=db, coproductionprocess=coproductionprocess_in)
    return coproductionprocess


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
    if not crud.coproductionprocess.can_update(current_user, coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    coproductionprocess = crud.coproductionprocess.update(db=db, db_obj=coproductionprocess, obj_in=coproductionprocess_in)
    return coproductionprocess


@router.get("/{id}", response_model=schemas.CoproductionProcessOutFull)
def read_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get coproductionprocess by ID.
    """
    coproductionprocess = crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(current_user, coproductionprocess):
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
    if not crud.coproductionprocess.can_remove(current_user, coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.coproductionprocess.remove(db=db, id=id)
    return None


# specific


@router.get("/{id}/phaseinstantiations/", response_model=List[schemas.PhaseInstantiationOut])
def list_related_phaseinstantiations(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve related phaseinstantiations.
    """
    coproductionprocess = crud.coproductionprocess.get(db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=400, detail="CoproductionProcess not found")
    return coproductionprocess.phaseinstantiations


@router.get("/{id}/tree", response_model=List[schemas.PhaseInstantiationOutFull])
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
    if not crud.coproductionprocess.can_remove(current_user, coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionprocess.phaseinstantiations