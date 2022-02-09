from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("", response_model=List[schemas.TaskOut])
def list_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve tasks.
    """
    if not crud.task.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    tasks = crud.task.get_multi(db, skip=skip, limit=limit)
    return tasks


@router.post("", response_model=schemas.TaskOutFull)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new task.
    """
    if not crud.task.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    task = crud.task.create(db=db, task=task_in)
    return task


@router.put("/{id}", response_model=schemas.TaskOutFull)
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    task_in: schemas.TaskPatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an task.
    """
    task = crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not crud.task.can_update(current_user, task):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    task = crud.task.update(db=db, db_obj=task, obj_in=task_in)
    return task


@router.get("/{id}", response_model=schemas.TaskOutFull)
def read_task(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get task by ID.
    """
    task = crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not crud.task.can_read(current_user, task):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return task

@router.get("/{id}/assets", response_model=List[schemas.AssetOutFull])
def read_task(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get task by ID.
    """
    task = crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not crud.task.can_read(current_user, task):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return task.assets

@router.delete("/{id}", response_model=schemas.TaskOutFull)
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an task.
    """
    task = crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not crud.task.can_remove(current_user, task):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.task.remove(db=db, id=id)
    return None