import uuid
from sqlalchemy.orm import Session
from typing import Optional
from app.models import Task, TaskInstantiation
from app.schemas import TaskCreate, TaskPatch, TaskInstantiationCreate, TaskInstantiationPatch
from app.general.utils.CRUDBase import CRUDBase
from app import crud, schemas

class CRUDTask(CRUDBase[Task, TaskCreate, TaskPatch]):

    def get_by_name(self, db: Session, name: str) -> Optional[Task]:
        return db.query(Task).filter(Task.name == name).first()

    def create(self, db: Session, *, task: TaskCreate) -> Task:
        db_obj = Task(
            name=task.name,
            description=task.description,
            is_public=task.is_public,
            objective_id=task.objective_id
        )
        db.add(db_obj)
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

class CRUDTaskInstantiation(CRUDBase[TaskInstantiation, TaskInstantiationCreate, TaskInstantiationPatch]):
    def create(self, db: Session, *, taskinstantiation: TaskInstantiationCreate) -> TaskInstantiation:
        db_obj = TaskInstantiation(
            objectiveinstantiation_id=taskinstantiation.objectiveinstantiation_id,
            task_id=taskinstantiation.task_id
        )
        db.add(db_obj)
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

crud_tasks = CRUDTask(Task)
crud_instantiations = CRUDTaskInstantiation(TaskInstantiation)
