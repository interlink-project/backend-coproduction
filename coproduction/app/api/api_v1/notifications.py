import os
import uuid
from typing import Any, List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from app import crud, models, schemas
from app.general import deps

router = APIRouter()


@router.get("", response_model=List[schemas.NotificationOutFull])
async def list_notifications(
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
  
) -> Any:
    return await crud.notification.get_multi(db=db, user=current_user)


@router.get("/{event}/notification", response_model=schemas.NotificationOutFull)
async def notification_by_event(
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
    event: str = '',
) -> Any:
    return await crud.notification.get_notification_by_event(db=db,event=event)


@router.post("", response_model=schemas.NotificationOutFull)
async def create_notification(
    *,
    db: Session = Depends(deps.get_db),
    notification_in: schemas.NotificationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new notification.
    """
    # notification = await crud.notification.get_by_name(db=db, name=notification_in.name)
    # if not notification:
    return await crud.notification.create(db=db, obj_in=notification_in)
    # raise HTTPException(status_code=400, detail="Notification already exists")




@router.put("/{id}", response_model=schemas.NotificationOutFull)
async def update_notification(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    notification_in: schemas.NotificationPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an notification.
    """
    notification = await crud.notification.get(db=db, id=id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return await crud.notification.update(db=db, db_obj=notification, obj_in=notification_in)




@router.get("/{id}", response_model=schemas.NotificationOutFull)
async def read_notification(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get notification by ID.
    """
    notification = await crud.notification.get(db=db, id=id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification




@router.delete("/{id}")
async def delete_notification(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an notification.
    """
    notification = await crud.notification.get(db=db, id=id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return await crud.notification.remove(db=db, id=id)


