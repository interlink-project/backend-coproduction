import json
import uuid
from typing import Dict, List
from app.general import deps
from app.usernotifications.crud import exportCrud as usernotification
from app.assets.crud import exportCrud as asset_crud
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, models, schemas

class NotificationsManager:
    def __init__(self):
        pass

    async def removeAsset(
        self, 
        id,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        ):

        #Save the event as a notification of coproduction
        print('El documento a borrar es:')
        print('id:'+str(id))
        db_obj = await asset_crud.get(db=db, id=id)
                        
        print(db_obj)
        if type(db_obj) == ExternalAssetCreate:
            #External Asset
            #Create the coproductionNotification
            notification = await notification_crud.get_notification_by_event(db=db, event="remove_asset_copro")
            if(notification):
                coproduction = await coproductionprocesses_crud.get(db=db, id=db_obj.coproductionprocess_id)
                task = await tasksCrud.get(db=db, id=db_obj.task_id)

                newCoproNotification=CoproductionProcessNotification()
                newCoproNotification.notification_id=notification.id
                newCoproNotification.coproductionprocess_id=coproduction.id

                # print(data)
                # print(db_obj.externalinterlinker)

                nameInterlinker='external'
                assetLink=asset.uri


                newCoproNotification.parameters="{'treeitem_id':'"+str(task.id)+"','treeItemName':'"+str(task.name)+"','assetId':'"+str(db_obj.id)+"','assetName':'"+asset.name+"','assetLink':'"+str(assetLink)+"','interlinkerName':'"+nameInterlinker+"','processName':'"+coproduction.name+"','userName':'"+shortName(db_obj.creator.full_name)+"','copro_id':'"+str(db_obj.coproductionprocess_id)+"'}"
                db.add(newCoproNotification)
        if type(db_obj) == InternalAssetCreate:
            
            #Internal Asset
            #Create the coproductionNotification
            notification = await notification_crud.get_notification_by_event(db=db, event="remove_asset_copro")
            
            if(notification):
                coproduction = await coproductionprocesses_crud.get(db=db, id=db_obj.coproductionprocess_id)
                task = await tasksCrud.get(db=db, id=db_obj.task_id)

                newCoproNotification=CoproductionProcessNotification()
                newCoproNotification.notification_id=notification.id
                newCoproNotification.coproductionprocess_id=coproduction.id

                nameInterlinker=''
                assetLink=''
                # print(db_obj)
                # print('Software:::')
                # print(db_obj.softwareinterlinker)

                assetLink=db_obj.link+'/view'
                if(db_obj.softwareinterlinker):
                    nameInterlinker=db_obj.softwareinterlinker['name']
                    

                else:
                    if(db_obj.knowledgeinterlinker):
                        nameInterlinker=db_obj.knowledgeinterlinker['name']

                
                newCoproNotification.parameters="{'treeitem_id':'"+str(task.id)+"','treeItemName':'"+str(task.name)+"','assetId':'"+str(db_obj.id)+"','assetName':'{assetid:"+str(db_obj.id)+"}','assetLink':'"+str(assetLink)+"','interlinkerName':'"+nameInterlinker+"','processName':'"+coproduction.name+"','userName':'"+shortName(db_obj.creator.full_name)+"','copro_id':'"+str(db_obj.coproductionprocess_id)+"'}"
                db.add(newCoproNotification)

        return None
        
  
    
notification_manager = NotificationsManager()