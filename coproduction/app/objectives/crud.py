import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.messages import log
from app.models import Objective, Phase, User, CoproductionProcessNotification
from app.schemas import ObjectiveCreate, ObjectivePatch
from app.treeitems.crud import exportCrud as treeitems_crud
from app.tasks.crud import exportCrud as tasks_crud
from app.notifications.crud import exportCrud as notification_crud
from app.coproductionprocesses.crud import exportCrud as coproductionprocesses_crud
from app.utils import recursive_check
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager
from app import models
import html


class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):
    async def create_from_metadata(self, db: Session, objectivemetadata: dict, phase: Phase, schema_id: uuid.UUID) -> Optional[Objective]:
        data = objectivemetadata.copy()
        del data["prerequisites_ids"]
        data["from_schema"] = schema_id
        data["from_item"] = data.get("id")
        creator = ObjectiveCreate(**data)
        return await self.create(db=db, obj_in=creator, commit=False, withNotifications=False, withSocketMsn=False, extra={
            "phase": phase
        })

    async def create(self, db: Session, *, obj_in: ObjectiveCreate, creator: User = None, extra: dict = {}, commit: bool = True, withNotifications: bool = True, withSocketMsn: bool = True) -> Objective:
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
                objective = await self.get(db=db, id=id)
                if objective:
                    await self.add_prerequisite(db=db, objective=db_obj, prerequisite=objective, commit=False)
        if postreqs:
            for id in postreqs:
                objective = await self.get(db=db, id=id)
                if objective:
                    await self.add_prerequisite(db=db, objective=objective, prerequisite=db_obj, commit=False)

        if commit:
            db.commit()
            db.refresh(db_obj)

         # Save the notifications:
        if (withNotifications):
            coproduction = await coproductionprocesses_crud.get(db=db, id=db_obj.coproductionprocess_id)
            notification = await notification_crud.get_notification_by_event(db=db, event="add_objective_copro", language=coproduction.language)
            if (notification):

                treeitem = await treeitems_crud.get(db=db, id=db_obj.id)

                newCoproNotification = CoproductionProcessNotification()
                newCoproNotification.notification_id = notification.id
                newCoproNotification.coproductionprocess_id = coproduction.id

                newCoproNotification.parameters = "{'objectiveName':'"+html.escape(db_obj.name)+"','processName':'"+html.escape(
                    coproduction.name)+"','treeitem_id':'"+str(treeitem.id)+"','copro_id':'"+str(db_obj.coproductionprocess_id)+"'}"

                db.add(newCoproNotification)
                db.commit()
                db.refresh(newCoproNotification)

        # In case there is another node with pre-requisite equal the one
        # of the objective it must change it prerequisite to the new id

        # Find other nodes wit the pre-requisite

        if prereqs:
            for id in prereqs:
                # Get all prerrequisites task with the id
                listObjectiveWithPrereq = db.query(Objective).filter(
                    models.Objective.prerequisites_ids == id).all()

                for objective in listObjectiveWithPrereq:
                    # Add the correct prerrequisite (the id of the new node)
                    if (objective.id != db_obj.id):
                        # Remove any previous prerrequisite
                        objective.prerequisites.clear()
                        # Append the just created node
                        objective.prerequisites.append(db_obj)
                        # Save in database
                        db.add(objective)
                        db.commit()
                        db.refresh(objective)

        if (withSocketMsn):
            await socket_manager.send_to_id(db_obj.coproductionprocess_id, {"event": "objective_created"})

        return db_obj

    async def add_prerequisite(self, db: Session, objective: Objective, prerequisite: Objective, commit: bool = True) -> Objective:
        if objective == prerequisite:
            print(objective, prerequisite)
            raise Exception("Same object")
        # TODO: if objective in prerequisite.prerequisites => block

        recursive_check(objective.id, prerequisite)
        objective.prerequisites.clear()
        objective.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(objective)
        return objective

    async def remove(self, db: Session, *, id: uuid.UUID, user_id: str = None, remove_definitely: bool = False, withNotifications: bool = True) -> Objective:
        obj = db.query(self.model).get(id)
        if not obj:
            raise Exception("Object does not exist")
        if remove_definitely:
            await self.log_on_remove(obj)
        else:
            await self.log_on_disable(obj)

        # Save the notifications:
        if (withNotifications):
            coproduction = await coproductionprocesses_crud.get(db=db, id=obj.coproductionprocess_id)
            notification = await notification_crud.get_notification_by_event(db=db, event="remove_objective_copro", language=coproduction.language)
            if (notification):

                treeitem = await treeitems_crud.get(db=db, id=obj.id)

                newCoproNotification = CoproductionProcessNotification()
                newCoproNotification.notification_id = notification.id
                newCoproNotification.coproductionprocess_id = coproduction.id

                # phase_treeitem_id   and  phaseName
                newCoproNotification.parameters = "{'phase_treeitem_id':'"+str(obj.phase.id)+"','phaseName':'"+html.escape(obj.phase.name)+"','objectiveName':'"+html.escape(
                    obj.name)+"','processName':'"+html.escape(coproduction.name)+"','copro_id':'"+str(obj.coproductionprocess_id)+"'}"

                db.add(newCoproNotification)
                db.commit()
                db.refresh(newCoproNotification)

        await treeitems_crud.remove(db=db, obj=obj, model=self.model, user_id=user_id, remove_definitely=remove_definitely)

    async def copy(self, db: Session, *, obj_in: ObjectiveCreate, coproductionprocess, parent: Phase, extra: dict = {}):
        print("COPYING OBJECTIVE", obj_in)

        # Get the new ids of the prerequistes
        prereqs_ids = []
        if obj_in.prerequisites_ids:
            for p_id in obj_in.prerequisites_ids:
                prereqs_ids.append(extra['Objective_'+str(p_id)])

        new_objective = ObjectiveCreate(
            id=uuid.uuid4(),
            name=obj_in.name,
            description=obj_in.description,
            phase_id=parent.id,
            phase=parent,
            coproductionprocess=coproductionprocess,
            prerequisites=obj_in.prerequisites,
            prerequisites_ids=prereqs_ids,
            status=obj_in.status,
            disabler_id=obj_in.disabler_id,
            disabled_on=obj_in.disabled_on,
            from_item=obj_in.from_item,
            from_schema=obj_in.from_schema
        )

        new_objective = await self.create(db=db, obj_in=new_objective, withNotifications=False)

        tasks_temp = obj_in.children.copy()
        tasks = []
        indexes = []

        for id, task in enumerate(tasks_temp):
            print('TASK', task)
            print(task.prerequisites_ids)
            if not len(task.prerequisites_ids):
                # if not task.is_disabled:
                tasks.append(task)
                indexes.append(str(task.id))
                tasks_temp.pop(id)

        def check_prerequistes(prereqs, list_indexes):
            for prereq in prereqs:
                if not str(prereq) in list_indexes:
                    return False
            return True

        while tasks_temp:
            for id, task in enumerate(tasks_temp):
                if check_prerequistes(task.prerequisites_ids, indexes):
                    tasks.append(task)
                    indexes.append(str(task.id))
                    tasks_temp.pop(id)
                    #    if not task.is_disabled:

        ids_dict = {}
        for child in tasks:
            tmp_task = await tasks_crud.copy(db=db, obj_in=child, coproductionprocess=coproductionprocess, parent=new_objective, extra=ids_dict)
            ids_dict['Task_'+str(child.id)] = tmp_task.id

        return new_objective, ids_dict

    async def log_on_disable(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "DISABLE"
        })
        await log(enriched)

    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "OBJECTIVE"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.phase.coproductionprocess_id
        logData["phase_id"] = obj.phase_id
        logData["objective_id"] = obj.id
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


exportCrud = CRUDObjective(Objective, logByDefault=True)
