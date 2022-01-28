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


@router.get("/", response_model=List[schemas.AssetOut])
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
        backend = interlinker["backend"]
        
    except:
        raise HTTPException(status_code=403, detail="Interlinker not found")

    try:
        print(f"http://{backend}/api/v1/assets/{asset_in.external_id}")
        assert requests.get(f"http://{backend}/api/v1/assets/{asset_in.external_id}").status_code == 200
        asset = crud.asset.create(db=db, asset=asset_in, external_id=asset_in.external_id)
        return asset
    except:
        raise HTTPException(status_code=403, detail="Error in interlinker")
    
        

@router.post("/with_file", response_model=schemas.AssetOutFull)
async def create_asset_with_file(
    *,
    f: UploadFile = File(...),
    params: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_active_user),


) -> Any:
    """
    Create new asset with file
    """
    try:
        dict_params = ast.literal_eval(params)
        asset_in = schemas.AssetCreate(**dict_params)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Asset schema not fulfilled")
    if not crud.asset.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    interlinker = crud.interlinker.get(
        db=db,
        id=dict_params["interlinker_id"]
    )
    if not interlinker:
        raise HTTPException(status_code=403, detail="Interlinker version not found")

    taskinstantiation = crud.taskinstantiation.get(
        db=db,
        id=dict_params["taskinstantiation_id"]
    )
    if not taskinstantiation:
        raise HTTPException(status_code=403, detail="Taskinstantiation not found")

    data = asset_in.__dict__

    files_data = {'file': (f.__dict__["filename"], f.file.read())}

    response = requests.post("http://filemanager/api/v1/assets/",
                             files=files_data, headers={}, data=data)

    data = response.json()
    external_id = data["id"]
    asset = crud.asset.create(
        db=db, asset=asset_in, name=interlinker.interlinker.name, external_id=external_id, backend="filemanager")
    
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
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not crud.asset.can_remove(current_user, asset):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.asset.remove(db=db, id=id)
    return None