import ast
import json
import uuid
from typing import Any, List, Optional

import requests
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps
from app.config import settings

router = APIRouter()


@router.get("", response_model=List[schemas.AssetOutFull])
def list_assets(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve assets.
    """
    if not crud.asset.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    assets = crud.asset.get_multi(db, skip=skip, limit=limit)
    return assets


@router.post("", response_model=schemas.AssetOutFull)
def create_asset(
    *,
    db: Session = Depends(deps.get_db),
    asset_in: schemas.AssetCreate,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new asset.
    """
    if not crud.asset.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # first check if task exists
    task = crud.task.get(db=db, id=asset_in.task_id)
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

    asset = crud.asset.create(db=db, asset=asset_in, coproductionprocess_id=task.objective.phase.coproductionprocess_id, creator=current_user)
    return asset

@router.post("/{id}/clone", response_model=schemas.AssetOutFull)
def clone_asset(
    *,
    id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Clone asset.
    """
    if not crud.asset.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    asset = crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # first check if task exists
    task = crud.task.get(db=db, id=asset.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    external_info = requests.post(asset.internal_link + "/clone", headers={
        "Authorization": "Bearer " + token
    }).json()
    print("EXTERNAL")
    print(external_info)
    external_id = external_info["id"] if "id" in external_info else external_info["_id"]
    asset = crud.asset.create(db=db, asset=schemas.AssetCreate(
        task_id=asset.task_id,
        softwareinterlinker_id=asset.softwareinterlinker_id,
        external_asset_id=external_id
    ), coproductionprocess_id=task.objective.phase.coproductionprocess_id, creator=current_user)
    return asset

@router.put("/{id}", response_model=schemas.AssetOutFull)
def update_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    asset_in: schemas.AssetPatch,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an asset.
    """
    asset = crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not crud.asset.can_update(current_user, asset):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    asset = crud.asset.update(db=db, db_obj=asset, obj_in=asset_in)
    return asset


@router.get("/{id}", response_model=schemas.AssetOutFull)
def read_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Get asset by ID.
    """
    asset = crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not crud.asset.can_read(current_user, asset):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return asset

@router.get("/external/{id}")
def read_external_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Get asset by ID.
    """
    asset = crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    print("Retrieving external ", asset.internal_link)
    return requests.get(asset.internal_link, headers={
        "Authorization": "Bearer " + token
    }).json()


@router.delete("/{id}", response_model=schemas.AssetOutFull)
def delete_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: dict = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an asset.
    """
    asset = crud.asset.get(db=db, id=id)
    # TODO: DELETE to interlinker
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not crud.asset.can_remove(current_user, asset):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.asset.remove(db=db, id=id)
    return None