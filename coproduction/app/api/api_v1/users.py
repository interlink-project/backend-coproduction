from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

router = APIRouter()

@router.post("", response_model=schemas.UserOutFull)
async def sync_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    # TODO: only from auth micro
    if user := await crud.user.get(db=db, id=user_in.id):
        return user
    return await crud.user.create(db=db, user=user_in)

