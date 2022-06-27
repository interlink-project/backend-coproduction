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

class CRUDTask(CRUDBase[Task, TaskCreate, TaskPatch]):
    async def create_from_metadata(self, db: Session, taskmetadata: dict, objective: Objective = None, schema_id = uuid.UUID) -> Optional[Task]:
        taskmetadata["problemprofiles"] = [pp["id"] for pp in taskmetadata.get("problemprofiles", [])]
        taskmetadata["from_schema"] = schema_id
        taskmetadata["from_item"] = taskmetadata.get("id")
        creator = TaskCreate(**taskmetadata)
        return await self.create(db=db, task=creator, commit=False, extra={
            "objective": objective,
        })

    async def add_prerequisite(self, db: Session, task: Task, prerequisite: Task, commit : bool = True) -> Task:
        if task == prerequisite:
            raise Exception("Same object")

        recursive_check(task.id, prerequisite)
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
