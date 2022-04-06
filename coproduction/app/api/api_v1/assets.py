import ast
import json
import uuid
from typing import Any, List, Optional

import requests
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps
from app.config import settings
from fastapi_pagination import Page

router = APIRouter()


@router.get("", response_model=Page[schemas.AssetOutFull])
async def list_assets(
    db: Session = Depends(deps.get_db),
    coproductionprocess_id: Optional[uuid.UUID] = Query(None),
    task_id: Optional[uuid.UUID] = Query(None),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve assets.
    """
    if not crud.asset.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.asset.get_multi_filtered(db, task_id=task_id, coproductionprocess_id=coproductionprocess_id)


@router.post("", response_model=schemas.AssetOutFull)
async def create_asset(
    *,
    db: Session = Depends(deps.get_db),
    asset_in: schemas.AssetCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new asset.
    """
    if not crud.asset.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # first check if task exists
    task = await crud.task.get(db=db, id=asset_in.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # check that interlinker in catalogue
    try:
        response = requests.get(f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/{asset_in.softwareinterlinker_id}", headers={
            "X-API-Key": "secret"
        })
        assert response.status_code == 200

    except:
        raise HTTPException(status_code=400, detail="Interlinker not active")

    asset = await crud.asset.create(
        db=db, asset=asset_in, coproductionprocess_id=task.objective.phase.coproductionprocess_id, creator=current_user)
    return asset


@router.post("/{id}/clone", response_model=schemas.AssetOutFull)
async def clone_asset(
    *,
    id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Clone asset.
    """
    if not crud.asset.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    asset = await crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # first check if task exists
    task = crud.task.get(db=db, id=asset.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        external_info = requests.post(asset.internal_link + "/clone", headers={
            "Authorization": "Bearer " + token
        }).json()
    except:
        external_info = requests.post(asset.link + "/clone", headers={
            "Authorization": "Bearer " + token
        }).json()

    external_id = external_info["id"] if "id" in external_info else external_info["_id"]
    asset = await crud.asset.create(db=db, asset=schemas.AssetCreate(
        task_id=asset.task_id,
        softwareinterlinker_id=asset.softwareinterlinker_id,
        knowledgeinterlinker_id=asset.knowledgeinterlinker_id,
        external_asset_id=external_id
    ), coproductionprocess_id=task.objective.phase.coproductionprocess_id, creator=current_user)
    return asset


@router.put("/{id}", response_model=schemas.AssetOutFull)
async def update_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    asset_in: schemas.AssetPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an asset.
    """
    asset = await crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not crud.asset.can_update(current_user, asset):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    asset = await crud.asset.update(db=db, db_obj=asset, obj_in=asset_in)
    return asset


@router.get("/{id}", response_model=schemas.AssetOutFull)
async def read_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get asset by ID.
    """
    
    if asset := await crud.asset.get(db=db, id=id):
        if not crud.asset.can_read(current_user, asset):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return asset
    raise HTTPException(status_code=404, detail="Asset not found")

@router.get("/external/{id}")
async def read_external_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Get asset by ID.
    """
    
    if asset := await crud.asset.get(db=db, id=id):
        print("Retrieving external ", asset.link)
        try:
            return requests.get(asset.internal_link, headers={
                "Authorization": "Bearer " + token
            }).json()
        except:
            return requests.get(asset.link, headers={
                "Authorization": "Bearer " + token
            }).json()
    raise HTTPException(status_code=404, detail="Asset not found")


@router.delete("/{id}", response_model=schemas.AssetOutFull)
async def delete_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an asset.
    """
    
    if asset := await crud.asset.get(db=db, id=id):
        if not crud.asset.can_remove(current_user, asset):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        await crud.asset.remove(db=db, id=id)
        return None
    # TODO: DELETE to interlinker
    raise HTTPException(status_code=404, detail="Asset not found")