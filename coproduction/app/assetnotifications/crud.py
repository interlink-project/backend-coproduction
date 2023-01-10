from app.messages import log
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Notification, AssetNotification, Asset, Organization
from app.schemas import NotificationCreate, NotificationPatch, AssetNotificationCreate, AssetNotificationPatch
import uuid
from app import models
from app.assets.crud import exportCrud as assets_crud

from sqlalchemy import or_, and_
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager
from uuid_by_string import generate_uuid
from app import schemas


class CRUDAssetNotification(CRUDBase[AssetNotification, AssetNotificationCreate, AssetNotificationPatch]):
    async def get_multi(self, db: Session, asset: Asset) -> Optional[List[AssetNotification]]:
        return db.query(AssetNotification).all()

    #Get all notifications by asset:
    async def get_asset_notifications(self, db: Session, asset_id: str) -> Optional[List[AssetNotification]]:
        listofAssetNotifications = db.query(AssetNotification).filter(models.AssetNotification.asset_id==asset_id).all();
        print(listofAssetNotifications)
        return listofAssetNotifications;


    async def create(self, db: Session, obj_in: AssetNotificationCreate) -> AssetNotification:
        obj_in_data = jsonable_encoder(obj_in)
        
        db_obj = AssetNotification(**obj_in_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        await socket_manager.broadcast({"event": "assetnotification_created"})

        await self.log_on_create(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        db_obj: AssetNotification,
        obj_in: schemas.AssetNotificationPatch
    ) -> AssetNotification:
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        await self.log_on_update(db_obj)
        return db_obj


exportCrud = CRUDAssetNotification(AssetNotification)