from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

from app.messages import log

router = APIRouter()


@router.get("", response_model=List[schemas.TaskOut])
async def list_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve tasks.
    """
    if not crud.task.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    tasks = await crud.task.get_multi(db, skip=skip, limit=limit)
    return tasks


@router.post("", response_model=schemas.TaskOutFull)
async def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new task.
    """
    if not crud.task.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    task = await crud.task.create(db=db, task=task_in)

    await log({
        "model": "TASK",
        "action": "CREATE",
        "crud": False,
        "coproductionprocess_id": task.objective.phase.coproductionprocess_id,
        "phase_id": task.objective.phase_id,
        "objective_id": task.objective_id,
        "task_id": task.id
    })

    return task


@router.put("/{id}", response_model=schemas.TaskOutFull)
async def update_task(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    task_in: schemas.TaskPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an task.
    """
    task = await crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not crud.task.can_update(current_user, task):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    task = await crud.task.update(db=db, db_obj=task, obj_in=task_in)

    await log({
        "model": "TASK",
        "action": "UPDATE",
        "crud": False,
        "coproductionprocess_id": task.objective.phase.coproductionprocess_id,
        "phase_id": task.objective.phase_id,
        "objective_id": task.objective_id,
        "task_id": task.id
    })

    return task


@router.get("/{id}", response_model=schemas.TaskOutFull)
async def read_task(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get task by ID.
    """
    task = await crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not crud.task.can_read(current_user, task):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await log({
        "model": "TASK",
        "action": "GET",
        "crud": False,
        "coproductionprocess_id": task.objective.phase.coproductionprocess_id,
        "phase_id": task.objective.phase_id,
        "objective_id": task.objective_id,
        "task_id": task.id
    })

    return task

@router.delete("/{id}", response_model=schemas.TaskOutFull)
async def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an task.
    """
    task = await crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not crud.task.can_remove(current_user, task):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await crud.task.remove(db=db, id=id)

    await log({
        "model": "TASK",
        "action": "DELETE",
        "crud": False,
        "coproductionprocess_id": task.objective.phase.coproductionprocess_id,
        "phase_id": task.objective.phase_id,
        "objective_id": task.objective_id,
        "task_id": task.id
    })

    return None