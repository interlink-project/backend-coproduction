from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("", response_model=List[schemas.MembershipOut])
def list_memberships(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: str = None,
    team_id: Optional[uuid.UUID] = None,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve memberships.
    """
    if not crud.membership.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if not user_id and not team_id:
        raise HTTPException(status_code=403, detail="Please, specify user_id or team_id")
    
    if user_id:
        memberships = crud.membership.get_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
    elif team_id:
        memberships = crud.membership.get_by_team_id(db, team_id=team_id, skip=skip, limit=limit)
    else:
        memberships = crud.membership.get_multi(db, skip=skip, limit=limit)
    return memberships


@router.post("", response_model=schemas.MembershipOutFull)
def create_membership(
    *,
    db: Session = Depends(deps.get_db),
    membership_in: schemas.MembershipCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new membership.
    """
    if not crud.membership.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    membership = crud.membership.create(db=db, membership=membership_in)
    return membership


@router.put("/{id}", response_model=schemas.MembershipOutFull)
def update_membership(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    membership_in: schemas.MembershipPatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an membership.
    """
    membership = crud.membership.get(db=db, id=id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    if not crud.membership.can_update(current_user, membership):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    membership = crud.membership.update(db=db, db_obj=membership, obj_in=membership_in)
    return membership


@router.get("/{id}", response_model=schemas.MembershipOutFull)
def read_membership(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Get membership by ID.
    """
    membership = crud.membership.get(db=db, id=id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    if not crud.membership.can_read(current_user, membership):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return membership


@router.delete("/{id}", response_model=schemas.MembershipOutFull)
def delete_membership(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an membership.
    """
    membership = crud.membership.get(db=db, id=id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    if not crud.membership.can_remove(current_user, membership):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.membership.remove(db=db, id=id)
    return None