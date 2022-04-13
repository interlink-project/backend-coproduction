from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

from app.messages import log

router = APIRouter()


@router.get("", response_model=List[schemas.PhaseOut])
async def list_phases(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve phases.
    """
    if not crud.phase.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    phase = await crud.phase.get_multi(db, skip=skip, limit=limit)

    return phase


@router.post("", response_model=schemas.PhaseOutFull)
async def create_phase(
    *,
    db: Session = Depends(deps.get_db),
    phase_in: schemas.PhaseCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new phase.
    """
    if not crud.phase.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    phase = await crud.phase.create(db=db, phase=phase_in)

    await log({
        "model": "PHASE",
        "action": "CREATE",
        "crud": False,
        "coproductionprocess_id": phase.coproductionprocess_id,
        "phase_id": phase.id
    })

    return phase



@router.get("/{id}/objectives", response_model=List[schemas.ObjectiveOut])
async def list_related_objectives(
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve related objectives.
    """
    phase = await crud.phase.get(db, id=id)
    if not phase:
        raise HTTPException(status_code=400, detail="Phase not found")
    return phase.objectives


@router.put("/{id}", response_model=schemas.PhaseOutFull)
async def update_phase(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    phase_in: schemas.PhasePatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an phase.
    """
    phase = await crud.phase.get(db=db, id=id)

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    if not crud.phase.can_update(current_user, phase):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    phase = await crud.phase.update(db=db, db_obj=phase, obj_in=phase_in)

    await log({
        "model": "PHASE",
        "action": "UPDATE",
        "crud": False,
        "coproductionprocess_id": phase.coproductionprocess_id,
        "phase_id": phase.id
    })

    return phase


@router.get("/{id}", response_model=schemas.PhaseOutFull)
async def read_phase(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get phase by ID.
    """
    phase = await crud.phase.get(db=db, id=id)

    await log({
        "model": "PHASE",
        "action": "GET",
        "crud": False,
        "coproductionprocess_id": phase.coproductionprocess_id,
        "phase_id": phase.id
    })
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    if not crud.phase.can_read(current_user, phase):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return phase


@router.delete("/{id}", response_model=schemas.PhaseOutFull)
async def delete_phase(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an phase.
    """
    phase = await crud.phase.get(db=db, id=id)

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    if not crud.phase.can_remove(current_user, phase):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await log({
        "model": "PHASE",
        "action": "DELETE",
        "crud": False,
        "coproductionprocess_id": phase.coproductionprocess_id,
        "phase_id": phase.id
    })
    await crud.phase.remove(db=db, id=id)
    return None