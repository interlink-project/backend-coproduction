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


@router.get("/", response_model=List[schemas.AssetOutFull])
def list_assets(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[dict] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve assets.
    """
    if not crud.asset.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    assets = crud.asset.get_multi(db, skip=skip, limit=limit)
    return assets


@router.post("/", response_model=schemas.AssetOutFull)
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

    # first check if taskinstantiation exists
    taskinstantiation = crud.taskinstantiation.get(
        db=db,
        id=asset_in.taskinstantiation_id
    )
    if not taskinstantiation:
        raise HTTPException(status_code=403, detail="Taskinstantiation not found")

    try:
        response = requests.get(f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/{asset_in.interlinker_id}")
        interlinker = response.json()
        path = interlinker["path"]
        
    except:
        raise HTTPException(status_code=500, detail="Interlinker not active")

    try:
        print(f"http://{path}/api/v1/assets/{asset_in.external_id}")
        assert requests.get(f"http://{path}/assets/{asset_in.external_id}").status_code == 200
        asset = crud.asset.create(db=db, asset=asset_in, external_id=asset_in.external_id)
        return asset
    except Exception as e:
        raise e
        raise HTTPException(status_code=500, detail="Error in interlinker")


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
    current_user: Optional[dict] = Depends(deps.get_current_user),
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