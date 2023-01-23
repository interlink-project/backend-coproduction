import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app import schemas
from app.general.utils.CRUDBase import CRUDBase
from app.models import Task, Phase, Objective, User
from app.schemas import TaskCreate, TaskPatch
from fastapi.encoders import jsonable_encoder
from app.utils import recursive_check, update_status_and_progress
from app.messages import log
from app.treeitems.crud import exportCrud as treeitems_crud
from app.sockets import socket_manager

class CRUDTask(CRUDBase[Task, TaskCreate, TaskPatch]):
    async def create_from_metadata(self, db: Session, taskmetadata: dict, objective: Objective = None, schema_id = uuid.UUID) -> Optional[Task]:
        data = taskmetadata.copy()
        del data["prerequisites_ids"]
        data["problemprofiles"] = [pp["id"] for pp in data.get("problemprofiles", [])]
        data["from_schema"] = schema_id
        data["from_item"] = data.get("id")
        creator = TaskCreate(**data)
        return await self.create(db=db, obj_in=creator, commit=False, extra={
            "objective": objective,
        })

    async def create(self, db: Session, *, obj_in: TaskCreate, creator: User = None, extra: dict = {}, commit: bool = True) -> Phase:
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
                task = await self.get(db=db, id=id)
                if task:
                   await self.add_prerequisite(db=db, task=db_obj, prerequisite=task, commit=False)
        if postreqs:
            for id in postreqs:
                task = await self.get(db=db, id=id)
                if task:
                   await self.add_prerequisite(db=db, task=task, prerequisite=db_obj, commit=False)
        if commit:
            db.commit()
            db.refresh(db_obj)

        await socket_manager.send_to_id(db_obj.coproductionprocess_id, {"event": "task_created"})
        return db_obj

    async def add_prerequisite(self, db: Session, task: Task, prerequisite: Task, commit : bool = True) -> Task:
        if task == prerequisite:
            print(task, prerequisite)
            raise Exception("Same object")

        recursive_check(task.id, prerequisite)
        task.prerequisites.clear()
        task.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(task)
        return task

    async def update(
        self,
        db: Session,
        db_obj: Task,
        obj_in: schemas.TaskPatch
    ) -> Task:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)

        if db_obj.objective:
            # update objective
            objective : Objective = db_obj.objective
            update_status_and_progress(objective)
            db.add(objective)

            # update phase
            phase : Phase = db_obj.objective.phase
            update_status_and_progress(phase)
            db.add(phase)

        db.commit()
        db.refresh(db_obj)
        await self.log_on_update(db_obj)
        await socket_manager.send_to_id(db_obj.coproductionprocess_id, {"event": "task_updated"})
        return db_obj

    async def remove(self, db: Session, *, id: uuid.UUID, user_id: str = None, remove_definitely: bool = False) -> Phase:
        obj = db.query(self.model).get(id)
        if not obj:
            raise Exception("Object does not exist")
        if remove_definitely:
            await self.log_on_remove(obj)
        else:
            await self.log_on_disable(obj)
        await treeitems_crud.remove(db=db, obj=obj, model=self.model, user_id=user_id, remove_definitely=remove_definitely)

    async def copy(self, db: Session, *, obj_in: TaskCreate, coproductionprocess, parent: Objective, extra: dict = {}) -> Task:
        print("COPYING TASK", obj_in)
        
        # Get the new ids of the prerequistes
        prereqs_ids = []
        if obj_in.prerequisites_ids:
            for p_id in obj_in.prerequisites_ids:
                prereqs_ids.append(extra['task_'+str(p_id)])
        
        new_task = TaskCreate(
                id=uuid.uuid4(),
                name=obj_in.name,
                description=obj_in.description,
                problemprofiles=obj_in.problemprofiles,
                objective_id=parent.id,
                objective=parent,
                start_date=obj_in.start_date,
                end_date=obj_in.end_date,
                coproductionprocess=coproductionprocess,
                prerequisites=obj_in.prerequisites,
                prerequisites_ids=prereqs_ids,
                status=obj_in.status,
                from_item=obj_in.from_item,
                from_schema=obj_in.from_schema
            )

        new_task = await self.create(db=db, obj_in=new_task)
        
        return new_task
    
    async def log_on_disable(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "DISABLE"
        })
        await log(enriched)
        
    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "TASK"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.objective.phase.coproductionprocess_id
        logData["phase_id"] = obj.objective.phase_id
        logData["objective_id"] = obj.objective_id
        logData["task_id"] = obj.id
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
        return user in object.coproductionprocess.administrators

    def can_remove(self, user, object):
        return user in object.coproductionprocess.administrators

exportCrud = CRUDTask(Task)
