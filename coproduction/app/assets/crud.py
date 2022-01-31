from sqlalchemy.orm import Session
from typing import List
from app.models import Asset
from app.schemas import AssetCreate, AssetPatch
from app.general.utils.CRUDBase import CRUDBase
from app import models
import uuid

class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetPatch]):
    def get_multi_by_taskinstantiation_id(
        self, db: Session, taskinstantiation_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        return db.query(Asset).filter(taskinstantiation_id=taskinstantiation_id).offset(skip).limit(limit).all()

    def create(self, db: Session, asset: AssetCreate, external_id: str) -> Asset:
        db_obj = Asset(
            taskinstantiation_id=asset.taskinstantiation_id,
            interlinker_id=asset.interlinker_id,
            external_id=external_id,
            icon=asset.icon,
            name=asset.name,
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: uuid.UUID) -> Asset:
        obj = db.query(Asset).get(id)
        db.delete(obj)
        db.commit()
        # TODO: remove from external microservice
        return obj

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