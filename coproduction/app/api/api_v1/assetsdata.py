import uuid
from typing import Any, List, Optional

import requests
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.general import deps

from app.messages import log
from app.notificationsManager import notification_manager

router = APIRouter()


# @router.get("", response_model=List[schemas.AssetsDataOutFull])
# async def read_assetsdatasdata(
#     db: Session = Depends(deps.get_db),
#     id: uuid.UUID,
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     return await crud.assetsdatasdata.get(db, id=id)

@router.get("", response_model=List[schemas.AssetsDataOutFull])
async def list_assetsdatas(
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
  
) -> Any:
    return await crud.assetsdata.get_multi(db=db)


@router.post("/create", response_model=schemas.AssetsDataOutFull)
async def create_assetsdata(
    *,
    db: Session = Depends(deps.get_db),
    assetsdata_in: schemas.AssetsDataCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new assetsdata.
    """
    print(assetsdata_in)
    return await crud.assetsdata.create(
        db=db, obj_in=assetsdata_in, creator=current_user)



@router.put("/{id}", response_model=schemas.AssetsDataOutFull)
async def update_assetsdata(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    assetsdata_in: schemas.AssetsDataPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an assetsdata.
    """
    assetsdata = await crud.assetsdata.get(db=db, id=id)
    if not assetsdata:
        raise HTTPException(status_code=404, detail="AssetsData not found")
    return await crud.assetsdata.update(db=db, db_obj=assetsdata, obj_in=assetsdata_in)


@router.get("/{id}", response_model=schemas.AssetsDataOutFull)
async def read_assetsdata(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    assetsdata_in: schemas.AssetsDataPatch,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get assetsdata by ID.
    """

    if assetsdata := await crud.assetsdata.get(db=db, id=id):
        return assetsdata
    raise HTTPException(status_code=404, detail="AssetsData not found")



@router.delete("/{id}")
async def delete_assetsdata(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an assetsdata.
    """

    if assetsdata := await crud.assetsdata.get(db=db, id=id):
        await crud.assetsdata.remove(db=db, id=id)
        return None

    # TODO: DELETE to interlinker
    raise HTTPException(status_code=404, detail="AssetsData not found")