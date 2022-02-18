from sqlalchemy.orm import Session
from typing import Optional
from app.models import CoproductionSchema, Phase
from app.schemas import CoproductionSchemaCreate, CoproductionSchemaPatch
from app.general.utils.CRUDBase import CRUDBase
from app import crud, schemas, models

class CRUDCoproductionSchema(CRUDBase[CoproductionSchema, CoproductionSchemaCreate, CoproductionSchemaPatch]):
    def get_public(self, db: Session, skip: int = 0, limit: int = 100) -> Optional[CoproductionSchema]:
        return db.query(CoproductionSchema).filter(CoproductionSchema.is_public == True).offset(skip).limit(limit).all()

    def get_by_name(self, db: Session, name: str, locale: str) -> Optional[CoproductionSchema]:
        return db.query(CoproductionSchema).filter(CoproductionSchema.name_translations[locale] == name).first()

    def create(self, db: Session, coproductionschema: CoproductionSchemaCreate) -> CoproductionSchema:
        db_obj = CoproductionSchema(
            name_translations=coproductionschema.name_translations,
            description_translations=coproductionschema.description_translations,
            is_public=coproductionschema.is_public,
            author=coproductionschema.author,
            licence=coproductionschema.licence,
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


exportCrud = CRUDCoproductionSchema(CoproductionSchema)
