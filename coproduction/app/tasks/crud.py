import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app import schemas
from app.general.utils.CRUDBase import CRUDBase
from app.general.utils.RowToDict import row2dict
from app.models import Task, Status, Phase, Objective
from app.schemas import TaskCreate, TaskPatch
from fastapi.encoders import jsonable_encoder

def calculate_status_and_progress(obj, key):
    statuses = [task.status for task in getattr(obj, key)]
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
    async def create_from_metadata(self, db: Session, taskmetadata: dict, objective: Objective = None, objective_id: uuid.UUID = None) -> Optional[Task]:
        if objective and objective_id:
            raise Exception("Specify only one objective")
        if not objective and not objective_id:
            raise Exception("Objective not specified")
        taskmetadata["problemprofiles"] = [pp["id"] for pp in taskmetadata.get("problemprofiles", [])]
        creator = TaskCreate(**taskmetadata, objective_id=objective_id)
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
        return db_obj

    async def add_prerequisite(self, db: Session, task: Task, prerequisite: Task, commit : bool = True) -> Task:
        if task == prerequisite:
            raise Exception("Same object")
        task.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(task)
        return task

    async def remove(self, db: Session, *, id: uuid.UUID) -> Task:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        related = db.query(Task).filter(Task.prerequisites.any(Task.id == obj.id)).all()
        for i in related:
            i.prerequisites.remove(obj)
        db.delete(obj)
        db.commit()
        return obj

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
            status, progress = calculate_status_and_progress(objective, "tasks")
            setattr(db_obj.objective, "status", status)
            setattr(db_obj.objective, "progress", progress)
            db.add(objective)

            # update phase
            phase : Phase = db_obj.objective.phase
            status, progress = calculate_status_and_progress(phase, "objectives")
            setattr(phase, "status", status)
            setattr(phase, "progress", progress)
            db.add(phase)

        db.commit()
        db.refresh(db_obj)
        return db_obj

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
