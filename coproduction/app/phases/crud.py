from sqlalchemy.orm import Session
from typing import Optional
from app.models import Phase, PhaseInstantiation, CoproductionSchema
from app.schemas import PhaseCreate, PhasePatch, PhaseInstantiationCreate, PhaseInstantiationPatch
from app.general.utils.CRUDBase import CRUDBase
from app import crud, schemas

class CRUDPhase(CRUDBase[Phase, PhaseCreate, PhasePatch]):

    def get_by_name(self, db: Session, name: str) -> Optional[Phase]:
        return db.query(Phase).filter(Phase.name == name).first()

    def create(self, db: Session, *, phase: PhaseCreate) -> Phase:
        db_obj = Phase(
            name=phase.name,
            description=phase.description,
            is_public=phase.is_public,
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


class CRUDPhaseInstantiation(CRUDBase[PhaseInstantiation, PhaseInstantiationCreate, PhaseInstantiationPatch]):
    def create(self, db: Session, *, phaseinstantiation: PhaseInstantiationCreate) -> PhaseInstantiation:
        db_obj = PhaseInstantiation(
            coproductionprocess_id=phaseinstantiation.coproductionprocess_id,
            phase_id=phaseinstantiation.phase_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        phase = crud.phases.get(db=db, id=phaseinstantiation.phase_id)
        for objective in phase.objectives:
            crud.objectiveinstantiation.create(
                db=db,
                objectiveinstantiation=schemas.ObjectiveInstantiationCreate(
                    objective_id=objective.id,
                    phaseinstantiation_id=db_obj.id
                )
            )
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


crud_phases = CRUDPhase(Phase)
crud_instantiations = CRUDPhaseInstantiation(PhaseInstantiation)
