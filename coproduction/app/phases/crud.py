from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Phase
from app.schemas import (
    PhaseCreate,
    PhasePatch,
)


class CRUDPhase(CRUDBase[Phase, PhaseCreate, PhasePatch]):

    def get_by_name(self, db: Session, name: str) -> Optional[Phase]:
        return db.query(Phase).filter(Phase.name == name).first()

    def create(self, db: Session, *, phase: PhaseCreate) -> Phase:
        db_obj = Phase(
            name_translations=phase.name_translations,
            description_translations=phase.description_translations,
            is_public=phase.is_public,
            # relations
            coproductionprocess_id=phase.coproductionprocess_id,
            coproductionschema_id=phase.coproductionschema_id,
            parent_id=phase.parent_id,
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


exportCrud = CRUDPhase(Phase)
