import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps

from app.messages import log

router = APIRouter()
    
@router.get("/{id}/permissions", response_model=schemas.PermissionOutFull)
async def get_permissions_of_treeitem(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get permission by ID.
    """
    if treeitem := await crud.treeitem.get(db=db, id=id):
        return await crud.permission.get_multi(db=db)
    raise HTTPException(status_code=404, detail="Permission not found")