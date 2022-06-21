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

router = APIRouter()


@router.get("", response_model=List[schemas.AssetOutFull])
async def list_assets(
    task_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    # coproductionprocess_id: Optional[uuid.UUID] = Query(None),
    current_user: Optional[models.User] = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve assets.
    """
    # check that task exists
    if not (task := await crud.task.get(db=db, id=task_id)):
        raise HTTPException(status_code=404, detail="Task not found")

    if not crud.asset.can_list(task):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return await crud.asset.get_multi(db, task=task)


def check_interlinker(id, token):
    url = f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/{id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    return response.json()


@router.post("", response_model=schemas.AssetOutFull)
async def create_asset(
    *,
    db: Session = Depends(deps.get_db),
    asset_in: schemas.AssetCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Create new asset.
    """
    # check that task exists
    if not (task := await crud.task.get(db=db, id=asset_in.task_id)):
        raise HTTPException(status_code=404, detail="Task not found")

    if not crud.asset.can_create(task):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # check that interlinker exists
    if type(asset_in) == schemas.InternalAssetCreate and asset_in.softwareinterlinker_id:
        softwareinterlinker = check_interlinker(asset_in.softwareinterlinker_id, token)

        if asset_in.knowledgeinterlinker_id:
            knowledgeinterlinker = check_interlinker(
                asset_in.knowledgeinterlinker_id, token)

    elif type(asset_in) == schemas.ExternalAssetCreate:
        if asset_in.externalinterlinker_id:
            interlinker = check_interlinker(asset_in.externalinterlinker_id, token)

    return await crud.asset.create(
        db=db, asset=asset_in, creator=current_user)


class InstantiateSchema(BaseModel):
    knowledgeinterlinker_id: uuid.UUID
    language: str
    task_id: uuid.UUID


@router.post("/instantiate", response_model=schemas.AssetOutFull)
async def instantiate_asset_from_knowledgeinterlinker(
    *,
    asset_in: InstantiateSchema,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Create new asset.
    """
    # first check if task exists
    if not (task := await crud.task.get(db=db, id=asset_in.task_id)):
        raise HTTPException(status_code=404, detail="Task not found")

    if not crud.asset.can_create(task):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Gets the knowledge interlinker
    response = requests.get(f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/{asset_in.knowledgeinterlinker_id}", headers={
        "Authorization": "Bearer " + token,
        "Accept-Language": asset_in.language
    })
    interlinker = response.json()

    if response.status_code == 404 or not interlinker:
        raise HTTPException(status_code=404, detail="Knowledge interlinker not found")

    # Clones the genesis asset of the knowledge interlinker by calling the software interlinker's (used by the knowledge) /clone method
    try:
        data_from_interlinker: dict = requests.post(interlinker.get("internal_link") + "/clone", headers={
            "Authorization": "Bearer " + token
        }).json()
    except:
        data_from_interlinker: dict = requests.post(interlinker.get("link") + "/clone", headers={
            "Authorization": "Bearer " + token
        }).json()

    external_asset_id = data_from_interlinker["id"] if "id" in data_from_interlinker else data_from_interlinker["_id"]
    # Creates an InternalAsset object with reference to the software interlinker that manages the asset, the knowledge interlinker that contained the genesis asset id and the id of the external resource
    return await crud.asset.create(db=db, creator=current_user, asset=schemas.InternalAssetCreate(
        **{
            "knowledgeinterlinker_id": asset_in.knowledgeinterlinker_id,
            "type": "internalasset",
            "softwareinterlinker_id": interlinker.get("softwareinterlinker_id"),
            "external_asset_id": external_asset_id,
            "task_id": task.id
        }
    ))


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
    # first check if task exists
    task: models.Task
    if not (task := await crud.task.get(db=db, id=asset.task_id)):
        raise HTTPException(status_code=404, detail="Task not found")

    if not crud.asset.can_create(task):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    asset: models.Asset
    if not (asset := await crud.asset.get(db=db, id=id)):
        raise HTTPException(status_code=404, detail="Asset not found")

    # TODO: check that the software interlinker of the original asset has the clone capability
    if asset.type == "internalasset":
        try:
            data_from_interlinker = requests.post(asset.internal_link + "/clone", headers={
                "Authorization": "Bearer " + token
            }).json()
        except:
            data_from_interlinker = requests.post(asset.link + "/clone", headers={
                "Authorization": "Bearer " + token
            }).json()

        external_asset_id = data_from_interlinker["id"] if "id" in data_from_interlinker else data_from_interlinker["_id"]

        asset: models.InternalAsset
        db_asset = await crud.asset.create(db=db, asset=schemas.InternalAssetCreate(
            task_id=asset.task_id,
            softwareinterlinker_id=asset.softwareinterlinker_id,
            knowledgeinterlinker_id=asset.knowledgeinterlinker_id,
            external_asset_id=external_asset_id
        ), creator=current_user)

    elif asset.type == "externalasset":
        asset: models.ExternalAsset
        db_asset = await crud.asset.create(db=db, asset=schemas.ExternalAssetCreate(
            task_id=asset.task_id,
            externalinterlinker_id=asset.externalinterlinker_id,
            name=asset.name,
            uri=asset.uri
        ), creator=current_user)

    else:
        raise HTTPException(status_code=500, detail="Asset type not recognized")

    return db_asset


@router.put("/{id}", response_model=schemas.AssetOutFull)
async def update_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    asset_in: schemas.AssetPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Update an asset.
    """
    asset = await crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not crud.asset.can_update(asset):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.asset.update(db=db, db_obj=asset, obj_in=asset_in)


@router.get("/{id}", response_model=schemas.AssetOutFull)
async def read_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    asset_in: schemas.AssetPatch,
    current_user: Optional[models.User] = Depends(deps.get_current_user),
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Get asset by ID.
    """

    if asset := await crud.asset.get(db=db, id=id):
        if not crud.asset.can_read(asset):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return asset
    raise HTTPException(status_code=404, detail="Asset not found")


@router.get("/internal/{id}")
async def read_internal_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    token: str = Depends(deps.get_current_active_token),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get asset by ID.
    """

    if asset := await crud.asset.get(db=db, id=id):
        if asset.type == "internalasset":
            if not crud.asset.can_read(asset):
                raise HTTPException(status_code=403, detail="Not enough permissions")

            print("Retrieving internal ", asset.link)
            await log(crud.asset.enrich_log_data(asset, {
                "action": "GET"
            }))
            try:
                return requests.get(asset.internal_link, headers={
                    "Authorization": "Bearer " + token
                }).json()
            except:
                return requests.get(asset.link, headers={
                    "Authorization": "Bearer " + token
                }).json()
        raise HTTPException(status_code=400, detail="Asset is not internal")
    raise HTTPException(status_code=404, detail="Asset not found")


@router.delete("/{id}")
async def delete_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token),
) -> Any:
    """
    Delete an asset.
    """

    if asset := await crud.asset.get(db=db, id=id):
        if not crud.asset.can_remove(asset):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        await crud.asset.remove(db=db, id=id)
        return None

    # TODO: DELETE to interlinker
    raise HTTPException(status_code=404, detail="Asset not found")