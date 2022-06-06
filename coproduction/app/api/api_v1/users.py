from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps
import requests

router = APIRouter()

@router.get("/me", response_model=schemas.UserOutFull)
async def me(
    *,
    db: Session = Depends(deps.get_db),
    token: str = Depends(deps.get_current_active_token)
) -> Any:
    """
    Get or create user.
    """
    cookies = {'auth_token': token}
    response = requests.get(f"http://auth/auth/api/v1/users/me", cookies=cookies, timeout=3)
    return await crud.user.get_or_create(db=db, data=response.json())