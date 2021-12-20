from sqlalchemy.orm import Session
from typing import Optional
from app.models import CoproductionSchema, Phase
from app.schemas import CoproductionSchemaCreate, CoproductionSchemaPatch
from app.general.utils.CRUDBase import CRUDBase
from app import crud

class CRUDCoproductionSchema(CRUDBase[CoproductionSchema, CoproductionSchemaCreate, CoproductionSchemaPatch]):

    def get_by_name(self, db: Session, name: str) -> Optional[CoproductionSchema]:
        return db.query(CoproductionSchema).filter(CoproductionSchema.name == name).first()

    def create(self, db: Session, *, coproductionschema: CoproductionSchemaCreate) -> CoproductionSchema:
        db_obj = CoproductionSchema(
            name=coproductionschema.name,
            description=coproductionschema.description,
            is_public=coproductionschema.is_public,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_phase(self, db: Session, *, coproductionschema: CoproductionSchema, phase: Phase) -> CoproductionSchema:            
        coproductionschema.phases.append(phase)
        db.commit()
        db.refresh(coproductionschema)
        return coproductionschema

    def remove_phase(self, db: Session, *, coproductionschema: CoproductionSchema, phase: Phase) -> CoproductionSchema:            
        coproductionschema.phases.remove(phase)
        db.commit()
        db.refresh(coproductionschema)
        return coproductionschema

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


exportCrud = CRUDCoproductionSchema(CoproductionSchema)
