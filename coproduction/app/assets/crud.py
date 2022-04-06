from sqlalchemy.orm import Session
from typing import List
from app.models import Asset
from app.schemas import AssetCreate, AssetPatch
from app.general.utils.CRUDBase import CRUDBase
from app import models
import uuid
from fastapi_pagination.ext.sqlalchemy import paginate
from app.messages import log

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
        db_obj = Asset(
            coproductionprocess_id=coproductionprocess_id,
            task_id=asset.task_id,
            knowledgeinterlinker_id=asset.knowledgeinterlinker_id,
            softwareinterlinker_id=asset.softwareinterlinker_id,
            external_asset_id=asset.external_asset_id,
            creator=creator
        )
        db.add(db_obj)
        db.commit()
        await log({
            "model": self.modelName,
            "action": "CREATE",
            "coproductionprocess_id": coproductionprocess_id,
            "task_id": db_obj.id
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