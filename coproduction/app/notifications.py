import json
import uuid
from typing import Dict, List
from app.general import deps
from app.usernotifications.crud import exportCrud as usernotification
import json

class NotificationManager:
    def __init__(self):
        pass

    def createUserNotification(
        self, 
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        ) => Any:
        print("Create a User Notification of the event", event)
        
        obj_in={
            "user_id": "123456"
            "notification_id": 123456
            "channel": "in_app"
            "state": False
            "parameters": null
        }
        
        usernotification.create(db: db, obj_in)



       
       

socket_manager = ConnectionManager()