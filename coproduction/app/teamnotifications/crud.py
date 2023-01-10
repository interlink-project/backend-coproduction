from app.messages import log
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Notification, TeamNotification, Team, Organization
from app.schemas import NotificationCreate, NotificationPatch, TeamNotificationCreate, TeamNotificationPatch
import uuid
from app import models
from app.teams.crud import exportCrud as teams_crud

from sqlalchemy import or_, and_
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager
from uuid_by_string import generate_uuid
from app import schemas


class CRUDTeamNotification(CRUDBase[TeamNotification, TeamNotificationCreate, TeamNotificationPatch]):
    async def get_multi(self, db: Session, team: Team) -> Optional[List[TeamNotification]]:
        return db.query(TeamNotification).all()

    #Get all notifications by team:
    async def get_team_notifications(self, db: Session, team_id: str) -> Optional[List[TeamNotification]]:
        listofTeamNotifications = db.query(TeamNotification).filter(models.TeamNotification.team_id==team_id).all();
        print(listofTeamNotifications)
        return listofTeamNotifications;


    async def create(self, db: Session, obj_in: TeamNotificationCreate) -> TeamNotification:
        obj_in_data = jsonable_encoder(obj_in)
        
        db_obj = TeamNotification(**obj_in_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        await socket_manager.broadcast({"event": "teamnotification_created"})

        await self.log_on_create(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        db_obj: TeamNotification,
        obj_in: schemas.TeamNotificationPatch
    ) -> TeamNotification:
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


exportCrud = CRUDTeamNotification(TeamNotification)