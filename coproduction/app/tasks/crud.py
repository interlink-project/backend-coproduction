import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, schemas
from app.general.utils.CRUDBase import CRUDBase
from app.general.utils.RowToDict import row2dict
from app.models import Task, TaskMetadata
from app.schemas import TaskCreate, TaskMetadataCreate, TaskMetadataPatch, TaskPatch


class CRUDTaskMetadata(CRUDBase[TaskMetadata, TaskMetadataCreate, TaskMetadataPatch]):

    def get_by_name(self, db: Session, name: str, language: str = "en") -> Optional[TaskMetadata]:
        return db.query(TaskMetadata).filter(TaskMetadata.name_translations[language] == name).first()

    def create(self, db: Session, *, taskmetadata: TaskMetadataCreate) -> TaskMetadata:
        db_obj = TaskMetadata(
            name_translations=taskmetadata.name_translations,
            description_translations=taskmetadata.description_translations,
            objectivemetadata_id=taskmetadata.objectivemetadata_id,
            problem_profiles=taskmetadata.problem_profiles
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

exportMetadataCrud = CRUDTaskMetadata(TaskMetadata)

class CRUDTask(CRUDBase[Task, TaskCreate, TaskPatch]):
    def create_from_metadata(self, db: Session, taskmetadata: TaskMetadata, objective_id: uuid.UUID, language: str) -> Optional[Task]:
        clone = row2dict(taskmetadata)
        clone["name"] = taskmetadata.name_translations[language]
        clone["description"] = taskmetadata.description_translations[language]
        creator = TaskCreate(**clone, objective_id=objective_id)
        return self.create(db=db, task=creator)

    def get_by_name(self, db: Session, name: str) -> Optional[Task]:
        return db.query(Task).filter(Task.name == name).first()

    def create(self, db: Session, *, task: TaskCreate) -> Task:
        db_obj = Task(
            name=task.name,
            description=task.description,
            objective_id=task.objective_id,
            problem_profiles=task.problem_profiles
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

exportCrud = CRUDTask(Task)
