from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.ObjectiveInstantiationOut])
def list_objectiveinstantiations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve objectiveinstantiations.
    """
    if not crud.objectiveinstantiation.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    objectiveinstantiations = crud.objectiveinstantiation.get_multi(db, skip=skip, limit=limit)
    return objectiveinstantiations


@router.post("/", response_model=schemas.ObjectiveInstantiationOutFull)
def create_objectiveinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    objectiveinstantiation_in: schemas.ObjectiveInstantiationCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new objectiveinstantiation.
    """
    if not crud.objectiveinstantiation.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    objectiveinstantiation = crud.objectiveinstantiation.create(db=db, objectiveinstantiation=objectiveinstantiation_in)
    return objectiveinstantiation


@router.put("/{id}", response_model=schemas.ObjectiveInstantiationOutFull)
def update_objectiveinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    objectiveinstantiation_in: schemas.ObjectiveInstantiationPatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an objectiveinstantiation.
    """
    objectiveinstantiation = crud.objectiveinstantiation.get(db=db, id=id)
    if not objectiveinstantiation:
        raise HTTPException(status_code=404, detail="ObjectiveInstantiation not found")
    if not crud.objectiveinstantiation.can_update(current_user, objectiveinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    objectiveinstantiation = crud.objectiveinstantiation.update(db=db, db_obj=objectiveinstantiation, obj_in=objectiveinstantiation_in)
    return objectiveinstantiation


@router.get("/{id}", response_model=schemas.ObjectiveInstantiationOutFull)
def read_objectiveinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get objectiveinstantiation by ID.
    """
    objectiveinstantiation = crud.objectiveinstantiation.get(db=db, id=id)
    if not objectiveinstantiation:
        raise HTTPException(status_code=404, detail="ObjectiveInstantiation not found")
    if not crud.objectiveinstantiation.can_read(current_user, objectiveinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return objectiveinstantiation


@router.delete("/{id}", response_model=schemas.ObjectiveInstantiationOutFull)
def delete_objectiveinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an objectiveinstantiation.
    """
    objectiveinstantiation = crud.objectiveinstantiation.get(db=db, id=id)
    if not objectiveinstantiation:
        raise HTTPException(status_code=404, detail="ObjectiveInstantiation not found")
    if not crud.objectiveinstantiation.can_remove(current_user, objectiveinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.objectiveinstantiation.remove(db=db, id=id)
    return None


@router.get("/{id}/taskinstantiations/", response_model=List[schemas.TaskInstantiationOut])
def list_related_taskinstantiations(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve related taskinstantiations.
    """
    objectiveinstantiation = crud.objectiveinstantiation.get(db, id=id)
    if not objectiveinstantiation:
        raise HTTPException(status_code=400, detail="ObjectiveInstantiation not found")
    return objectiveinstantiation.taskinstantiations
