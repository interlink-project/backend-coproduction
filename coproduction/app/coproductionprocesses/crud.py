import uuid
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from app import crud, schemas
from app.models import CoproductionProcess, CoproductionSchema
from app.schemas import CoproductionProcessCreate, CoproductionProcessPatch
from app.general.utils.CRUDBase import CRUDBase


class CRUDCoproductionProcess(CRUDBase[CoproductionProcess, CoproductionProcessCreate, CoproductionProcessPatch]):
    def get_by_artefact(self, db: Session, artefact_id: uuid.UUID) -> Optional[CoproductionProcess]:
        return db.query(CoproductionProcess).filter(CoproductionProcess.artefact_id == artefact_id).first()

    def create(self, db: Session, *, coproductionprocess: CoproductionProcessCreate, schema: Optional[CoproductionSchema]) -> CoproductionProcess:
        
        db_obj = CoproductionProcess(
            artefact_id=coproductionprocess.artefact_id,
            team_id=coproductionprocess.team_id,
            name=coproductionprocess.name,
            logotype=coproductionprocess.logotype,
            description=coproductionprocess.description,
            aim=coproductionprocess.aim,
            idea=coproductionprocess.idea,
            organization=coproductionprocess.organization,
            challenges=coproductionprocess.challenges,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Create all phases
        if not schema:
            schema = crud.coproductionschema.get_by_name(db=db, name="MAIN_SCHEMA")
        for ph in schema.phases:
            crud.phaseinstantiation.create(
                db=db,
                phaseinstantiation=schemas.PhaseInstantiationCreate(
                    coproductionprocess_id=db_obj.id,
                    phase_id=ph.id
                )
            )

        # TODO: Create all roles
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


exportCrud = CRUDCoproductionProcess(CoproductionProcess)
