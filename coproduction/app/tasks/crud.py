import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app import schemas
from app.general.utils.CRUDBase import CRUDBase
from app.models import Task, Status, Phase, Objective
from app.schemas import TaskCreate, TaskPatch
from fastapi.encoders import jsonable_encoder
from app.utils import recursive_check

def calculate_status_and_progress(obj):
    statuses = [task.status for task in getattr(obj, "children")]
    status = Status.awaiting
    if all([x == Status.finished for x in statuses]):
        status = Status.finished
    elif all([x == Status.awaiting for x in statuses]):
        status = Status.awaiting
    else:
        status = Status.in_progress
    countInProgress = statuses.count(Status.in_progress) / 2
    countFinished = statuses.count(Status.finished)
    length = len(statuses)
    progress = int((countInProgress + countFinished) * 100 / length) if length > 0 else 0
    return status, progress

class CRUDTask(CRUDBase[Task, TaskCreate, TaskPatch]):
    async def create_from_metadata(self, db: Session, taskmetadata: dict, objective: Objective = None) -> Optional[Task]:
        taskmetadata["problemprofiles"] = [pp["id"] for pp in taskmetadata.get("problemprofiles", [])]
        creator = TaskCreate(**taskmetadata)
        return await self.create(db=db, task=creator, objective=objective, commit=False)

    async def get_by_name(self, db: Session, name: str) -> Optional[Task]:
        return db.query(Task).filter(Task.name == name).first()

    async def create(self, db: Session, *, task: TaskCreate, objective: Objective = None, commit : bool = True) -> Task:
        if objective and task.objective_id:
            raise Exception("Specify only one objective")
        if not objective and not task.objective_id:
            raise Exception("Objective not specified")
        
        db_obj = Task(
            name=task.name,
            description=task.description,
            objective=objective,
            objective_id=task.objective_id,
            problemprofiles=task.problemprofiles,
            start_date=task.start_date,
            end_date=task.end_date
        )
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
            await self.log_on_create(db_obj)
        return db_obj

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
            status, progress = calculate_status_and_progress(objective)
            setattr(db_obj.objective, "status", status)
            setattr(db_obj.objective, "progress", progress)
            db.add(objective)

            # update phase
            phase : Phase = db_obj.objective.phase
            status, progress = calculate_status_and_progress(phase)
            setattr(phase, "status", status)
            setattr(phase, "progress", progress)
            db.add(phase)

        db.commit()
        db.refresh(db_obj)
        await self.log_on_update(db_obj)
        return db_obj

    # Override log methods
    def enrich_log_data(self, obj, logData):
        logData["model"] = "TASK"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.objective.phase.coproductionprocess_id
        logData["phase_id"] = obj.objective.phase_id
        logData["objective_id"] = obj.objective_id
        logData["task_id"] = obj.id
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

exportCrud = CRUDTask(Task)
