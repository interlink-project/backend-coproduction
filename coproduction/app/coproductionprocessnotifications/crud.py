from app.messages import log
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from app.general.utils.CRUDBase import CRUDBase
from app.models import Notification, CoproductionProcessNotification, User, Organization
from app.schemas import NotificationCreate, NotificationPatch, CoproductionProcessNotificationCreate, CoproductionProcessNotificationPatch
import uuid
from app import models
from app.users.crud import exportCrud as users_crud
from app.assets.crud import exportCrud as assets_crud
from app.treeitems.crud import exportCrud as treeitems_crud

from sqlalchemy import or_, and_
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager
from uuid_by_string import generate_uuid
from app import schemas
import json


class CRUDCoproductionProcessNotification(CRUDBase[CoproductionProcessNotification, CoproductionProcessNotificationCreate, CoproductionProcessNotificationPatch]):
    async def get_multi(self, db: Session, user: User) -> Optional[List[CoproductionProcessNotification]]:
        return db.query(CoproductionProcessNotification).all()

    #Get all notifications by user:
    async def get_coproductionprocess_notifications(self, db: Session, coproductionprocess_id: str,user) -> Optional[List[CoproductionProcessNotification]]:
        
        listofCoproductionProcessNotifications = db.query(CoproductionProcessNotification).filter(models.CoproductionProcessNotification.coproductionprocess_id==coproductionprocess_id).order_by(models.CoproductionProcessNotification.created_at.desc()).all()
        
        #Filtrar las notificaciones a las que tengo permisos:
        for notification in listofCoproductionProcessNotifications:
            if notification.asset_id:
                asset=await assets_crud.get(db=db,id=notification.asset_id)
                tienePermisosListado=assets_crud.can_list(db=db,user=user,task=asset.task)
                #Remove the notification a user dont have permissions
                if not tienePermisosListado:
                    listofCoproductionProcessNotifications.remove(notification)

        return listofCoproductionProcessNotifications

    async def get_coproductionprocess_notifications_byAseetId(self, db: Session, coproductionprocess_id: str, asset_id:str) -> Optional[List[CoproductionProcessNotification]]:
        listofCoproductionProcessNotifications = db.query(CoproductionProcessNotification).filter(and_(
                                                                                                        models.CoproductionProcessNotification.coproductionprocess_id==coproductionprocess_id,
                                                                                                        models.CoproductionProcessNotification.asset_id==asset_id
                                                                                                        )                                                                                             
                                                                                                    ).order_by(models.CoproductionProcessNotification.created_at.desc()).all()
        #print(listofCoproductionProcessNotifications)
        return listofCoproductionProcessNotifications

    async def get_coproductionprocess_notifications_justbyAseetId(self, db: Session, asset_id:str) -> Optional[List[CoproductionProcessNotification]]:
        listofCoproductionProcessNotifications = db.query(CoproductionProcessNotification).filter(models.CoproductionProcessNotification.asset_id==asset_id                                                                                             
                                                                                                    ).order_by(models.CoproductionProcessNotification.created_at.desc()).all()
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
    
    async def updateAssetNameParameter(
        self,
        db: Session,
        asset_id: str,
        name: str, 
        coproductionprocess_id: str
    ) -> Optional[List[CoproductionProcessNotification]]:

        resultNot=db.query(models.CoproductionProcessNotification).filter(models.CoproductionProcessNotification.coproductionprocess_id==coproductionprocess_id).all()
        
        #Loop all notifications of the coproduction process
        for copronot in resultNot:
            
            #Set the dinamic parameters
            parametersJson= json.loads(copronot.parameters.replace("'", '"'))

            if( 'assetName' in json.dumps(parametersJson)):

                parametersJson['assetName']=parametersJson['assetName'].replace('{assetid:'+asset_id+'}', name)
                parametersJson['assetLink']=''
                parametersJson['showIcon']='hidden'
                parametersJson['showLink']=''

                copronot.parameters=json.dumps(parametersJson)

                #copronot.parameters=copronot.parameters.replace('{assetid:'+asset_id+'}', name)
                #print('resp '+copronot.parameters)
                db.add(copronot)
        
        
        db.commit()
        #print('Se ha reemplazado exitosamente los nombres: '+str(asset_id)+' por '+name)
        
        return


exportCrud = CRUDCoproductionProcessNotification(CoproductionProcessNotification)