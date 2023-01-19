from app.messages import log
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Notification, UserNotification, User, Organization
from app.schemas import NotificationCreate, NotificationPatch, UserNotificationCreate, UserNotificationPatch
import uuid
from app import models
from app.users.crud import exportCrud as users_crud

from sqlalchemy import or_, and_
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager
from uuid_by_string import generate_uuid
from app import schemas


class CRUDUserNotification(CRUDBase[UserNotification, UserNotificationCreate, UserNotificationPatch]):
    async def get_multi(self, db: Session, user: User) -> Optional[List[UserNotification]]:
        return db.query(UserNotification).all()

    #Get all notifications by user:
    async def get_user_notifications(self, db: Session, user_id: str) -> Optional[List[UserNotification]]:
        listofUserNotifications = db.query(UserNotification).filter(models.UserNotification.user_id==user_id).all()
        print(listofUserNotifications)
        return listofUserNotifications

    #Get unseen notifications by user:
    async def get_unseen_user_notifications(self, db: Session, user_id: str) -> Optional[List[UserNotification]]:
        listofUserNotifications = db.query(UserNotification).filter(
            and_(models.UserNotification.user_id==user_id,models.UserNotification.state==False)
            ).order_by(models.UserNotification.created_at.desc()).all()
        print(listofUserNotifications)
        return listofUserNotifications

    #Set seen to all notifications by user:
    async def set_seen_all_user_notifications(self, db: Session, user_id: str) -> Optional[List[UserNotification]]:
        db.query(models.UserNotification).filter(models.UserNotification.user_id.hex == user_id).update({'state': True})
        db.commit()
        #print(user_id)
        
        return


    async def create(self, db: Session, obj_in: UserNotificationCreate) -> UserNotification:
        obj_in_data = jsonable_encoder(obj_in)
        
        db_obj = UserNotification(**obj_in_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        await socket_manager.broadcast({"event": "usernotification_created"})

        await self.log_on_create(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        db_obj: UserNotification,
        obj_in: schemas.UserNotificationPatch
    ) -> UserNotification:
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


exportCrud = CRUDUserNotification(UserNotification)