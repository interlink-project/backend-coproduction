from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("", response_model=List[schemas.ObjectiveOut])
def list_objectives(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve objectives.
    """
    if not crud.objective.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    objectives = crud.objective.get_multi(db, skip=skip, limit=limit)
    return objectives


@router.post("", response_model=schemas.ObjectiveOutFull)
def create_objective(
    *,
    db: Session = Depends(deps.get_db),
    objective_in: schemas.ObjectiveCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new objective.
    """
    if not crud.objective.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    objective = crud.objective.create(db=db, objective=objective_in)
    return objective


@router.get("/{id}/tasks", response_model=List[schemas.TaskOut])
def list_related_tasks(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve related tasks.
    """
    objective = crud.objective.get(db, id=id)
    if not objective:
        raise HTTPException(status_code=400, detail="Objective not found")
    return objective.tasks


@router.put("/{id}", response_model=schemas.ObjectiveOutFull)
def update_objective(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    objective_in: schemas.ObjectivePatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an objective.
    """
    objective = crud.objective.get(db=db, id=id)
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    if not crud.objective.can_update(current_user, objective):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    objective = crud.objective.update(db=db, db_obj=objective, obj_in=objective_in)
    return objective


@router.get("/{id}", response_model=schemas.ObjectiveOutFull)
def read_objective(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get objective by ID.
    """
    objective = crud.objective.get(db=db, id=id)
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    if not crud.objective.can_read(current_user, objective):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return objective


@router.delete("/{id}", response_model=schemas.ObjectiveOutFull)
def delete_objective(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an objective.
    """
    objective = crud.objective.get(db=db, id=id)
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    if not crud.objective.can_remove(current_user, objective):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.objective.remove(db=db, id=id)
    return None

