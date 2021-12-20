from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.TaskInstantiationOut])
def list_taskinstantiations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve taskinstantiations.
    """
    if not crud.taskinstantiation.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    taskinstantiations = crud.taskinstantiation.get_multi(db, skip=skip, limit=limit)
    return taskinstantiations


@router.post("/", response_model=schemas.TaskInstantiationOutFull)
def create_taskinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    taskinstantiation_in: schemas.TaskInstantiationCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new taskinstantiation.
    """
    if not crud.taskinstantiation.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    taskinstantiation = crud.taskinstantiation.create(db=db, taskinstantiation=taskinstantiation_in)
    return taskinstantiation


@router.put("/{id}", response_model=schemas.TaskInstantiationOutFull)
def update_taskinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    taskinstantiation_in: schemas.TaskInstantiationPatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an taskinstantiation.
    """
    taskinstantiation = crud.taskinstantiation.get(db=db, id=id)
    if not taskinstantiation:
        raise HTTPException(status_code=404, detail="TaskInstantiation not found")
    if not crud.taskinstantiation.can_update(current_user, taskinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    taskinstantiation = crud.taskinstantiation.update(db=db, db_obj=taskinstantiation, obj_in=taskinstantiation_in)
    return taskinstantiation


@router.get("/{id}", response_model=schemas.TaskInstantiationOutFull)
def read_taskinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get taskinstantiation by ID.
    """
    taskinstantiation = crud.taskinstantiation.get(db=db, id=id)
    if not taskinstantiation:
        raise HTTPException(status_code=404, detail="TaskInstantiation not found")
    if not crud.taskinstantiation.can_read(current_user, taskinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return taskinstantiation


@router.delete("/{id}", response_model=schemas.TaskInstantiationOutFull)
def delete_taskinstantiation(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an taskinstantiation.
    """
    taskinstantiation = crud.taskinstantiation.get(db=db, id=id)
    if not taskinstantiation:
        raise HTTPException(status_code=404, detail="TaskInstantiation not found")
    if not crud.taskinstantiation.can_remove(current_user, taskinstantiation):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.taskinstantiation.remove(db=db, id=id)
    return None