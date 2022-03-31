from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Objective
from app.schemas import (
    ObjectiveCreate,
    ObjectivePatch
)
import uuid
from app.general.utils.RowToDict import row2dict

class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):
    def create_from_metadata(self, db: Session, objectivemetadata: dict, phase_id: uuid.UUID) -> Optional[Objective]:
        creator = ObjectiveCreate(**objectivemetadata, phase_id=phase_id)
        return self.create(db=db, objective=creator)

    def get_by_name(self, db: Session, name: str) -> Optional[Objective]:
        return db.query(Objective).filter(Objective.name == name).first()

    def create(self, db: Session, *, objective: ObjectiveCreate) -> Objective:
        db_obj = Objective(
            name=objective.name,
            description=objective.description,
            progress=objective.progress,
            # relations
            phase_id=objective.phase_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_prerequisite(self, db: Session, objective: Objective, prerequisite: Objective) -> Objective:
        if objective.id == prerequisite.id:
            raise Exception("Same object")
        objective.prerequisites.append(prerequisite)
        db.commit()
        db.refresh(objective)
        return objective

    def remove(self, db: Session, *, id: uuid.UUID) -> Objective:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        related = db.query(Objective).filter(Objective.prerequisites.any(Objective.id == obj.id)).all()
        for i in related:
            i.prerequisites.remove(obj)
        db.delete(obj)
        db.commit()
        return obj

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


exportCrud = CRUDObjective(Objective)
