from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Objective
from app.schemas import (
    ObjectiveCreate,
    ObjectivePatch,
)


class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):

    def get_by_name(self, db: Session, name: str) -> Optional[Objective]:
        return db.query(Objective).filter(Objective.name == name).first()

    def create(self, db: Session, *, objective: ObjectiveCreate) -> Objective:
        db_obj = Objective(
            is_public=objective.is_public,
            name_translations=objective.name_translations,
            description_translations=objective.description_translations,
            progress=objective.progress,
            start_date=objective.start_date,
            end_date=objective.end_date,
            # relations
            phase_id=objective.phase_id,
            parent_id=objective.parent_id
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


exportCrud = CRUDObjective(Objective)
