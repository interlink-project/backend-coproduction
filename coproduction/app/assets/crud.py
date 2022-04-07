from sqlalchemy.orm import Session
from typing import List
from app.models import Asset, InternalAsset, ExternalAsset
from app.schemas import AssetCreate, AssetPatch, ExternalAssetCreate, InternalAssetCreate
from app.general.utils.CRUDBase import CRUDBase
from app import models
import uuid
from fastapi_pagination.ext.sqlalchemy import paginate
from app.messages import log
from fastapi.encoders import jsonable_encoder

class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetPatch]):

    async def get_multi_filtered(
        self, db: Session, coproductionprocess_id: uuid.UUID, task_id: uuid.UUID
    ) -> List[Asset]:
        queries = []
        if coproductionprocess_id:
            queries.append(Asset.coproductionprocess_id == coproductionprocess_id)
        
        if task_id:
            queries.append(Asset.task_id == task_id)
        await log({
            "model": self.modelName,
            "action": "LIST",
            "coproductionprocess_id": coproductionprocess_id,
            "task_id": task_id
        })
        return paginate(db.query(Asset).filter(*queries))
    
    async def create(self, db: Session, asset: AssetCreate, coproductionprocess_id: uuid.UUID, creator: models.User) -> Asset:
        data = jsonable_encoder(asset)
        if type(asset) == ExternalAssetCreate:
            print("IS EXTERNAL")
            data["type"] = "externalasset"
            db_obj = ExternalAsset(**data)

        if type(asset) == InternalAssetCreate:
            print("IS INTERNAL")
            data["type"] = "internalasset"
            db_obj = InternalAsset(**data)

        db.add(db_obj)
        db.commit()
        await log({
            "model": self.modelName,
            "action": "CREATE",
            "id": db_obj.id,
            "coproductionprocess_id": coproductionprocess_id,
            "task_id": db_obj.task.id
        })
        db.refresh(db_obj)
        db_obj.set_links()
        return db_obj
    
    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def can_read(self, user, object):
        return True

    def can_update(self, user, object):
        return True

    def can_remove(self, user, object):
        return True

exportCrud = CRUDAsset(Asset)