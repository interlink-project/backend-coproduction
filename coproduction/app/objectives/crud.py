from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Objective, Phase
from app.schemas import (
    ObjectiveCreate,
    ObjectivePatch
)
import uuid
from app.general.utils.RowToDict import row2dict

class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):
    def create_from_metadata(self, db: Session, objectivemetadata: dict, phase: Phase = None, phase_id: uuid.UUID = None) -> Optional[Objective]:
        if phase and phase_id:
            raise Exception("Specify only one phase")
        if not phase and not phase_id:
            raise Exception("Phase not specified")
        creator = ObjectiveCreate(**objectivemetadata, phase_id=phase_id)
        return self.create(db=db, objective=creator, phase=phase, commit=False)

    def get_by_name(self, db: Session, name: str) -> Optional[Objective]:
        return db.query(Objective).filter(Objective.name == name).first()

    def create(self, db: Session, *, objective: ObjectiveCreate, phase: Phase = None, commit : bool = True) -> Objective:
        if phase and objective.phase_id:
            raise Exception("Specify only one objective")
        if not phase and not objective.phase_id:
            raise Exception("Objective not specified")
        db_obj = Objective(
            name=objective.name,
            description=objective.description,
            progress=objective.progress,
            # relations
            phase=phase,
            phase_id=objective.phase_id,
        )
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def add_prerequisite(self, db: Session, objective: Objective, prerequisite: Objective, commit : bool = True) -> Objective:
        if objective == prerequisite:
            raise Exception("Same object")
        # TODO: if objective in prerequisite.prerequisites => block
        objective.prerequisites.append(prerequisite)
        if commit:
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
