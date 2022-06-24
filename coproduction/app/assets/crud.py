from fastapi import HTTPException
import requests
from sqlalchemy.orm import Session
from typing import List
from app.models import Asset, InternalAsset, ExternalAsset
from app.tasks.crud import exportCrud as tasksCrud
from app.schemas import AssetCreate, AssetPatch, ExternalAssetCreate, InternalAssetCreate
from app.general.utils.CRUDBase import CRUDBase
from app import models
import uuid
from app.messages import log
from fastapi.encoders import jsonable_encoder
import favicon
from app.tasks.crud import update_status_and_progress

class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetPatch]):
    async def get_multi(
        self, db: Session, task: models.Task, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        queries = []
        if task:
            queries.append(Asset.task_id == task.id)
        return db.query(Asset).filter(*queries).offset(skip).limit(limit).all()

    async def create(self, db: Session, asset: AssetCreate, creator: models.User, task: models.Task) -> Asset:
        data = jsonable_encoder(asset)
        if type(asset) == ExternalAssetCreate:
            print("IS EXTERNAL")
            data["type"] = "externalasset"

            # try to get favicon
            try:
                icons = favicon.get(asset.uri)
                if len(icons) > 0 and (icon := icons[0]) and icon.format:
                    response = requests.get(icon.url, stream=True)

                    icon_path = f'/app/static/assets/{uuid.uuid4()}.{icon.format}'
                    with open(icon_path, 'wb') as image:
                        for chunk in response.iter_content(1024):
                            image.write(chunk)
                    icon_path = icon_path.replace("/app", "")
                    print(icon_path)
                    data["icon_path"] = icon_path
            except:
                pass
            db_obj = ExternalAsset(**data, creator=creator, objective_id=task.objective_id, phase_id=task.objective.phase_id, coproductionprocess_id=task.objective.phase.coproductionprocess_id)

        if type(asset) == InternalAssetCreate:
            print("IS INTERNAL")
            data["type"] = "internalasset"
            db_obj = InternalAsset(**data, creator=creator, objective_id=task.objective_id, phase_id=task.objective.phase_id, coproductionprocess_id=task.objective.phase.coproductionprocess_id)

        

        db.add(db_obj)
        db.commit()
        task : models.Task = db_obj.task
        if task.status == models.Status.awaiting:
            task.status = models.Status.in_progress
            db.add(task)
            update_status_and_progress(task.objective)
            db.add(task.objective)
            update_status_and_progress(task.objective.phase)
            db.add(task.objective.phase)
            db.commit()
            
        db.refresh(db_obj)
        await self.log_on_create(db_obj)
        return db_obj

    # Override log methods
    def enrich_log_data(self, asset, logData):
        logData["model"] = "ASSET"
        logData["object_id"] = asset.id
        logData["type"] = asset.type
        logData["phase_id"] = asset.task.objective.phase_id
        logData["objective_id"] = asset.task.objective_id
        logData["task_id"] = asset.task_id
        logData["coproductionprocess_id"] = asset.task.objective.phase.coproductionprocess_id
        logData["roles"] = asset.task.user_roles

        if type(asset) == models.InternalAsset:
            if ki := asset.knowledgeinterlinker:
                logData["knowledgeinterlinker_id"] = ki.get("id")
                logData["knowledgeinterlinker_name"] = ki.get("name")
            if si := asset.softwareinterlinker:
                logData["softwareinterlinker_id"] = si.get("id")
                logData["softwareinterlinker_name"] = si.get("name")
        elif type(asset) == models.ExternalAsset:
            if ei := asset.externalinterlinker:
                logData["externalinterlinker_id"] = ei.get("id")
                logData["externalinterlinker_name"] = ei.get("name")
        return logData

    # CRUD Permissions

    def can_create(self, task: models.TreeItem):
        return task.user_can(permission="create_assets_permission")

    def can_list(self, task: models.TreeItem):
        return task.user_can(permission="access_assets_permission")

    def can_read(self, asset: Asset):
        return asset.task.user_can(permission="access_assets_permission")

    def can_update(self, asset: Asset):
        return asset.task.user_can(permission="create_assets_permission")

    def can_remove(self, asset: Asset):
        return asset.task.user_can(permission="delete_assets_permission")


exportCrud = CRUDAsset(Asset, logByDefault=True)
