from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

from pydantic import BaseModel
from app.messages import log

router = APIRouter()

class LogsCreate(BaseModel):
    action: str
    model: str
    object_id: str


@router.post("")
async def insert_log(
    *,
    db: Session = Depends(deps.get_db),
    log_in: LogsCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Insert new log
    """

    await log({
        "model": log_in.model,
        "action": log_in.action.upper(),
        "frontend": True,
        "object_id": log_in.object_id
    })

    return True



