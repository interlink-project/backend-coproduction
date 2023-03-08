import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app import models
from app.general.utils.CRUDBase import CRUDBase
from app.messages import log
from app.models import CoproductionProcess, Phase, User, CoproductionProcessNotification
from app.schemas import PhaseCreate, PhasePatch
from app.treeitems.crud import exportCrud as treeitems_crud
from app.objectives.crud import exportCrud as objectives_crud
from app.notifications.crud import exportCrud as notification_crud
from app.coproductionprocesses.crud import exportCrud as coproductionprocesses_crud
from app.utils import recursive_check
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager
from app import models

class CRUDPhase(CRUDBase[Phase, PhaseCreate, PhasePatch]):
    async def create_from_metadata(self, db: Session, phasemetadata: dict, coproductionprocess: CoproductionProcess, schema_id: uuid.UUID) -> Optional[Phase]:
        data = phasemetadata.copy()
        del data["prerequisites_ids"]
        data["from_schema"] = schema_id
        data["from_item"] = data.get("id")
        creator = PhaseCreate(**data)
        return await self.create(db=db, obj_in=creator, commit=False,withNotifications=False,withSocketMsn=False, extra={
            "coproductionprocess": coproductionprocess
        })

    async def create(self, db: Session, *, obj_in: PhaseCreate, creator: User = None, extra: dict = {}, commit: bool = True, withNotifications : bool = True, withSocketMsn : bool = True) -> Phase:
        
        print('Llega a create la Phase!!')
        obj_in_data = jsonable_encoder(obj_in)
        prereqs = obj_in_data.get("prerequisites_ids")
        del obj_in_data["prerequisites_ids"]
        postreqs = obj_in_data.get("postrequisites_ids")
        del obj_in_data["postrequisites_ids"]

        db_obj = self.model(**obj_in_data, **extra)  # type: ignore

        if creator:
            db_obj.creator_id = creator.id
        
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
            await self.log_on_create(db_obj)
            
        if prereqs:
            for id in prereqs:
                phase = await self.get(db=db, id=id)
                if phase:
                   await self.add_prerequisite(db=db, phase=db_obj, prerequisite=phase)
        if postreqs:
            for id in postreqs:
                phase = await self.get(db=db, id=id)
                if phase:
                   await self.add_prerequisite(db=db, phase=phase, prerequisite=db_obj, commit=False)
                   
        if commit:
            db.commit()
            db.refresh(db_obj)


        # In case there is another node with pre-requisite equal the one 
        # of the phase it must change it prerequisite to the new id
        
        # Find other nodes wit the pre-requisite
 
        if prereqs:
            for id in prereqs:
                #Get all prerrequisites phase with the id
                listPhaseWithPrereq=db.query(Phase).filter(models.Phase.prerequisites_ids==id).all()
                
                for phase in listPhaseWithPrereq:
                    #Add the correct prerrequisite (the id of the new node)
                    if(phase.id!=db_obj.id):
                        #Remove any previous prerrequisite
                        phase.prerequisites.clear()
                        #Append the just created node
                        phase.prerequisites.append(db_obj)
                        #Save in database
                        db.add(phase)
                        db.commit()
                        db.refresh(phase)
        
        #Save the notifications:
        if(withNotifications):
            coproduction = await coproductionprocesses_crud.get(db=db, id=db_obj.coproductionprocess_id)
            notification = await notification_crud.get_notification_by_event(db=db, event="add_phase_copro",language=coproduction.language)
            if(notification):
                
                treeitem = await treeitems_crud.get(db=db, id=db_obj.id)
                
                newCoproNotification=CoproductionProcessNotification()
                newCoproNotification.notification_id=notification.id
                newCoproNotification.coproductionprocess_id=coproduction.id

                newCoproNotification.parameters="{'phaseName':'"+db_obj.name+"','processName':'"+coproduction.name+"','treeitem_id':'"+str(treeitem.id)+"','copro_id':'"+str(db_obj.coproductionprocess_id)+"'}"

                db.add(newCoproNotification)
                db.commit()
                db.refresh(newCoproNotification)

        if(withSocketMsn):
            await socket_manager.send_to_id(db_obj.coproductionprocess_id, {"event": "phase_created"})
        
        return db_obj
            
    async def add_prerequisite(self, db: Session, phase: Phase, prerequisite: Phase, commit: bool = True) -> Phase:
        if phase == prerequisite:
            print(phase, prerequisite)
            raise Exception("Same object")

        recursive_check(phase.id, prerequisite)
        phase.prerequisites.clear()
        phase.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(phase)
        return phase

    async def remove(self, db: Session, *, id: uuid.UUID, user_id: str = None, remove_definitely: bool = False, withNotifications : bool = True) -> Phase:
        obj = db.query(self.model).get(id)
        if not obj:
            raise Exception("Object does not exist")
        if remove_definitely:
            await self.log_on_remove(obj)
        else:
            await self.log_on_disable(obj)
        
        #Save the notifications:
        if(withNotifications):
            coproduction = await coproductionprocesses_crud.get(db=db, id=obj.coproductionprocess_id)
            notification = await notification_crud.get_notification_by_event(db=db, event="remove_phase_copro",language=coproduction.language)
            if(notification):
                
                treeitem = await treeitems_crud.get(db=db, id=obj.id)
                
                newCoproNotification=CoproductionProcessNotification()
                newCoproNotification.notification_id=notification.id
                newCoproNotification.coproductionprocess_id=coproduction.id

                newCoproNotification.parameters="{'phaseName':'"+obj.name+"','processName':'"+coproduction.name+"','copro_id':'"+str(obj.coproductionprocess_id)+"'}"

                db.add(newCoproNotification)
                db.commit()
                db.refresh(newCoproNotification)

        
        
        await treeitems_crud.remove(db=db, obj=obj, model=self.model, user_id=user_id, remove_definitely=remove_definitely)

        



    async def copy(self, db: Session, *, obj_in: PhaseCreate, coproductionprocess: CoproductionProcess,creator: User = None, extra: dict = {}, commit: bool = True):
        print("copying phase")
        
        # Get the new ids of the prerequistes
        prereqs_ids = []
        if obj_in.prerequisites_ids:
            for p_id in obj_in.prerequisites_ids:
                prereqs_ids.append(extra['Phase_'+str(p_id)])

        new_phase = PhaseCreate(
                progress=obj_in.progress,
                status=obj_in.status,
                disabler_id= obj_in.disabler_id,
                disabled_on= obj_in.disabled_on,
                id=uuid.uuid4(),
                from_item=obj_in.from_item,
                name=obj_in.name,
                is_part_of_codelivery=obj_in.is_part_of_codelivery,
                from_schema=obj_in.from_schema,
                description=obj_in.description,
                coproductionprocess_id=coproductionprocess.id,
                prerequisites=obj_in.prerequisites,
                prerequisites_ids=prereqs_ids
            )
            
        new_phase = await self.create(db=db, obj_in=new_phase,withNotifications=False)
        
        objectives_temp = obj_in.children.copy()
        objectives = []
        for id, objective in enumerate(objectives_temp):
            if not objective.prerequisites_ids:
                #if not objective.is_disabled:
                    objectives.append(objective)
                    objectives_temp.pop(id)
        
        while objectives_temp:
            for id, objective in enumerate(objectives_temp):
                if str(objective.prerequisites_ids[0]) == str(objectives[-1].id):
                    #if not objective.is_disabled:
                        objectives.append(objective)
                        objectives_temp.pop(id)
        
        #  Create a dict with the old ids and the new ids
        ids_dict = {}
        for child in objectives:
            tmp_obj, obj_id_updates = await objectives_crud.copy(db=db, obj_in=child, coproductionprocess=coproductionprocess, parent=new_phase, extra=ids_dict)
            ids_dict['Objective_'+str(child.id)] = tmp_obj.id
            ids_dict.update(obj_id_updates)
            
        return new_phase, ids_dict

    async def log_on_disable(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "DISABLE"
        })
        await log(enriched)

    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "PHASE"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.coproductionprocess_id
        logData["phase_id"] = obj.id
        logData["roles"] = obj.user_roles
        return logData

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


exportCrud = CRUDPhase(Phase, logByDefault=True)
