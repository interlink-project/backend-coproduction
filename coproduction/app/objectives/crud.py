from sqlalchemy.orm import Session
from typing import Optional
from app.models import Objective, ObjectiveInstantiation
from app.schemas import ObjectiveCreate, ObjectivePatch, ObjectiveInstantiationCreate, ObjectiveInstantiationPatch
from app.general.utils.CRUDBase import CRUDBase
from app import crud, schemas
class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):

    def get_by_name(self, db: Session, name: str) -> Optional[Objective]:
        return db.query(Objective).filter(Objective.name == name).first()

    def create(self, db: Session, *, objective: ObjectiveCreate) -> Objective:
        db_obj = Objective(
            name=objective.name,
            description=objective.description,
            is_public=objective.is_public,
            phase_id=objective.phase_id
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

class CRUDObjectiveInstantiation(CRUDBase[ObjectiveInstantiation, ObjectiveInstantiationCreate, ObjectiveInstantiationPatch]):
    def create(self, db: Session, *, objectiveinstantiation: ObjectiveInstantiationCreate) -> ObjectiveInstantiation:
        db_obj = ObjectiveInstantiation(
            phaseinstantiation_id=objectiveinstantiation.phaseinstantiation_id,
            objective_id=objectiveinstantiation.objective_id,
            progress=objectiveinstantiation.progress,
            start_date=objectiveinstantiation.start_date,
            end_date=objectiveinstantiation.end_date
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        objective = crud.objective.get(db=db, id=objectiveinstantiation.objective_id)
        for task in objective.tasks:
            crud.taskinstantiation.create(
                db=db,
                taskinstantiation=schemas.TaskInstantiationCreate(
                    task_id=task.id,
                    objectiveinstantiation_id=db_obj.id
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

crud_objectives = CRUDObjective(Objective)
crud_instantiations = CRUDObjectiveInstantiation(ObjectiveInstantiation)
