import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.messages import log
from app.models import Objective, Phase, User
from app.schemas import ObjectiveCreate, ObjectivePatch
from app.treeitems.crud import exportCrud as treeitems_crud
from app.tasks.crud import exportCrud as tasks_crud
from app.utils import recursive_check
from fastapi.encoders import jsonable_encoder
from app.sockets import socket_manager

class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):
    async def create_from_metadata(self, db: Session, objectivemetadata: dict, phase: Phase, schema_id: uuid.UUID) -> Optional[Objective]:
        data = objectivemetadata.copy()
        del data["prerequisites_ids"]
        data["from_schema"] = schema_id
        data["from_item"] = data.get("id")
        creator = ObjectiveCreate(**data)
        return await self.create(db=db, obj_in=creator, commit=False, extra={
            "phase": phase
        })
    
    async def create(self, db: Session, *, obj_in: ObjectiveCreate, creator: User = None, extra: dict = {}, commit: bool = True) -> Objective:
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

        await socket_manager.send_to_id(db_obj.coproductionprocess_id, {"event": "phase_created"})
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

    async def remove(self, db: Session, *, id: uuid.UUID, user_id: str = None, remove_definitely: bool = False) -> Objective:
        obj = db.query(self.model).get(id)
        if not obj:
            raise Exception("Object does not exist")
        if remove_definitely:
            await self.log_on_remove(obj)
        else:
            await self.log_on_disable(obj)
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
                from_item=obj_in.from_item,
                from_schema=obj_in.from_schema
            )

        new_objective = await self.create(db=db, obj_in=new_objective)
        
        tasks_temp = obj_in.children.copy()
        tasks = []
        for id, task in enumerate(tasks_temp):
            if not task.prerequisites_ids:
                tasks.append(task)
                tasks_temp.pop(id)
        
        while tasks_temp:
            for id, task in enumerate(tasks_temp):
                if str(task.prerequisites_ids[0]) == str(tasks[-1].id):
                    tasks.append(task)
                    tasks_temp.pop(id)

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
