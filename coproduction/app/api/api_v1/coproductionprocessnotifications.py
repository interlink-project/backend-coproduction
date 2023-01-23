import os
import uuid
from typing import Any, List, Optional

import aiofiles
import json
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from app import crud, models, schemas
from app.general import deps
from app.models import CoproductionProcessNotification

router = APIRouter()


@router.get("", response_model=List[schemas.CoproductionProcessNotificationOutFull])
async def list_coproductionprocessnotifications(
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
  
) -> Any:
    return await crud.coproductionprocessnotification.get_multi(db=db, user=current_user)

@router.get("/{coproductionprocess_id}/listCoproductionProcessNotifications", response_model=List[schemas.CoproductionProcessNotificationOutFull])
async def list_coproductionprocessnotifications(
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
    coproductionprocess_id: str = '',
) -> Any:
    return await crud.coproductionprocessnotification.get_coproductionprocess_notifications(db=db,coproductionprocess_id=coproductionprocess_id)

# @router.get("/users/{username}", tags=["users"])
# async def read_user(username: str):
#     return {"username": username}

@router.post("", response_model=schemas.CoproductionProcessNotificationOutFull)
async def create_coproductionprocessnotification(
    *,
    db: Session = Depends(deps.get_db),
    coproductionprocessnotification_in: schemas.CoproductionProcessNotificationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new coproductionprocessnotification.
    """
    # coproductionprocessnotification = await crud.coproductionprocessnotification.get_by_name(db=db, name=coproductionprocessnotification_in.name)
    # if not coproductionprocessnotification:
    return await crud.coproductionprocessnotification.create(db=db, obj_in=coproductionprocessnotification_in)
    # raise HTTPException(status_code=400, detail="CoproductionProcessNotification already exists")

@router.post("/createbyEvent", response_model=schemas.CoproductionProcessNotificationOutFull)
async def create_copro_notification(
    *,
    db: Session = Depends(deps.get_db),
    coproductionprocessnotification_in: schemas.CoproductionProcessNotificationCreatebyEvent,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new coproductionprocessnotification.
    """
    notification = await crud.notification.get_notification_by_event(db=db, event=coproductionprocessnotification_in.notification_event)
    newCoproNotification=CoproductionProcessNotification()
    newCoproNotification.notification_id=notification.id
    newCoproNotification.coproductionprocess_id=coproductionprocessnotification_in.coproductionprocess_id

    #Add the user to the information
    import json

    def shortName(s):
        # split the string into a list
        l = s.split()
        new = ""
        # traverse in the list
        for i in range(len(l)-1):
            s = l[i]
            # adds the capital first character
            new += (s[0].upper()+'.')
        
        # l[-1] gives last item of list l. We
        # use title to print first character in
        # capital.
        new += l[-1].title()
        return new

    json_parameters = json.loads(coproductionprocessnotification_in.parameters)
    json_parameters['userName']=shortName(current_user.full_name)
    newCoproNotification.parameters=json.dumps(json_parameters)

    return await crud.coproductionprocessnotification.create(db=db, obj_in=newCoproNotification)




@router.put("/updateAssetNameParameter/{asset_id}", response_model=schemas.CoproductionProcessNotificationOutFull)
async def create_coproductionprocessnotification(
    *,
    db: Session = Depends(deps.get_db),
    asset_id: str,
    name: str,
    coproductionprocess_id: str = '',
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new coproductionprocessnotification.
    """
    return await crud.coproductionprocessnotification.updateAssetNameParameter(db=db, asset_id=asset_id,name=name,coproductionprocess_id=coproductionprocess_id)
    


@router.put("/{id}", response_model=schemas.CoproductionProcessNotificationOutFull)
async def update_coproductionprocessnotification(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    coproductionprocessnotification_in: schemas.CoproductionProcessNotificationPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an coproductionprocessnotification.
    """
    coproductionprocessnotification = await crud.coproductionprocessnotification.get(db=db, id=id)

    if not coproductionprocessnotification:
        raise HTTPException(status_code=404, detail="CoproductionProcessNotification not found")
    return await crud.coproductionprocessnotification.update(db=db, db_obj=coproductionprocessnotification, obj_in=coproductionprocessnotification_in)



@router.get("/{id}/coproductionprocessnotification", response_model=schemas.CoproductionProcessNotificationOutFull)
async def read_coproductionprocessnotification(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get coproductionprocessnotification by ID.
    """
    coproductionprocessnotification = await crud.coproductionprocessnotification.get(db=db, id=id)
    if not coproductionprocessnotification:
        raise HTTPException(status_code=404, detail="CoproductionProcessNotification not found")
    return coproductionprocessnotification

@router.get("/{id}/notification")
async def get_coproductionprocessnotification_notification(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocessnotification notification.
    """
    coproductionprocessnotification = await crud.coproductionprocessnotification.get(db=db, id=id)
    if not coproductionprocessnotification:
        raise HTTPException(status_code=404, detail="Usernotification not found")
    return coproductionprocessnotification.notification




@router.delete("/{id}")
async def delete_coproductionprocessnotification(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an coproductionprocessnotification.
    """
    coproductionprocessnotification = await crud.coproductionprocessnotification.get(db=db, id=id)
    if not coproductionprocessnotification:
        raise HTTPException(status_code=404, detail="CoproductionProcessNotification not found")
    return await crud.coproductionprocessnotification.remove(db=db, id=id)

