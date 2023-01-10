from app.messages import log
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Notification, CoproductionProcessNotification, User, Organization
from app.schemas import NotificationCreate, NotificationPatch, CoproductionProcessNotificationCreate, CoproductionProcessNotificationPatch
import uuid
from app import models
from app.users.crud import exportCrud as users_crud

from sqlalchemy import or_, and_
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager
from uuid_by_string import generate_uuid
from app import schemas


class CRUDCoproductionProcessNotification(CRUDBase[CoproductionProcessNotification, CoproductionProcessNotificationCreate, CoproductionProcessNotificationPatch]):
    async def get_multi(self, db: Session, user: User) -> Optional[List[CoproductionProcessNotification]]:
        return db.query(CoproductionProcessNotification).all()

    #Get all notifications by user:
    async def get_coproductionprocess_notifications(self, db: Session, coproductionprocess_id: str) -> Optional[List[CoproductionProcessNotification]]:
        listofCoproductionProcessNotifications = db.query(CoproductionProcessNotification).filter(models.CoproductionProcessNotification.coproductionprocess_id==coproductionprocess_id).all()
        print(listofCoproductionProcessNotifications)
        return listofCoproductionProcessNotifications


    async def create(self, db: Session, obj_in: CoproductionProcessNotificationCreate) -> CoproductionProcessNotification:
        obj_in_data = jsonable_encoder(obj_in)
        
        db_obj = CoproductionProcessNotification(**obj_in_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        await socket_manager.broadcast({"event": "coproductionprocessnotification_created"})

        await self.log_on_create(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        db_obj: CoproductionProcessNotification,
        obj_in: schemas.CoproductionProcessNotificationPatch
    ) -> CoproductionProcessNotification:
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


exportCrud = CRUDCoproductionProcessNotification(CoproductionProcessNotification)