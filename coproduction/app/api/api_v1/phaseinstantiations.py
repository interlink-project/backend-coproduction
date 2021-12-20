from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.PhaseInstantiationOut])
def list_phaseinstantiations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve phaseinstantiations.
    """
    if not crud.phaseinstantiation.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    phaseinstantiations = crud.phaseinstantiation.get_multi(db, skip=skip, limit=limit)
    return phaseinstantiations


@router.post("/", response_model=schemas.PhaseInstantiationOutFull)
def create_phaseinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    phaseinstantiation_in: schemas.PhaseInstantiationCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new phaseinstantiation.
    """
    if not crud.phaseinstantiation.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    phaseinstantiation = crud.phaseinstantiation.create(db=db, phaseinstantiation=phaseinstantiation_in)
    return phaseinstantiation


@router.put("/{id}", response_model=schemas.PhaseInstantiationOutFull)
def update_phaseinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    phaseinstantiation_in: schemas.PhaseInstantiationPatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an phaseinstantiation.
    """
    phaseinstantiation = crud.phaseinstantiation.get(db=db, id=id)
    if not phaseinstantiation:
        raise HTTPException(status_code=404, detail="PhaseInstantiation not found")
    if not crud.phaseinstantiation.can_update(current_user, phaseinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    phaseinstantiation = crud.phaseinstantiation.update(db=db, db_obj=phaseinstantiation, obj_in=phaseinstantiation_in)
    return phaseinstantiation


@router.get("/{id}", response_model=schemas.PhaseInstantiationOutFull)
def read_phaseinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get phaseinstantiation by ID.
    """
    phaseinstantiation = crud.phaseinstantiation.get(db=db, id=id)
    if not phaseinstantiation:
        raise HTTPException(status_code=404, detail="PhaseInstantiation not found")
    if not crud.phaseinstantiation.can_read(current_user, phaseinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return phaseinstantiation


@router.delete("/{id}", response_model=schemas.PhaseInstantiationOutFull)
def delete_phaseinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an phaseinstantiation.
    """
    phaseinstantiation = crud.phaseinstantiation.get(db=db, id=id)
    if not phaseinstantiation:
        raise HTTPException(status_code=404, detail="PhaseInstantiation not found")
    if not crud.phaseinstantiation.can_remove(current_user, phaseinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.phaseinstantiation.remove(db=db, id=id)
    return None


@router.get("/{id}/objectiveinstantiations/", response_model=List[schemas.ObjectiveInstantiationOut])
def list_related_objectiveinstantiations(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve related objectiveinstantiations.
    """
    phaseinstantiation = crud.phaseinstantiation.get(db, id=id)
    if not phaseinstantiation:
        raise HTTPException(status_code=400, detail="PhaseInstantiation not found")
    return phaseinstantiation.objectiveinstantiations
