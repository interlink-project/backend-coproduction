from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Objective, ObjectiveMetadata
from app.schemas import (
    ObjectiveCreate,
    ObjectivePatch,
    ObjectiveMetadataCreate,
    ObjectiveMetadataPatch
)
import uuid
from app.general.utils.RowToDict import row2dict

class CRUDObjectiveMetadata(CRUDBase[ObjectiveMetadata, ObjectiveMetadataCreate, ObjectiveMetadataPatch]):

    def get_by_name(self, db: Session, name: str, language: str = "en") -> Optional[ObjectiveMetadata]:
        return db.query(ObjectiveMetadata).filter(ObjectiveMetadata.name_translations[language] == name).first()

    def create(self, db: Session, *, objectivemetadata: ObjectiveMetadataCreate) -> ObjectiveMetadata:
        db_obj = ObjectiveMetadata(
            name_translations=objectivemetadata.name_translations,
            description_translations=objectivemetadata.description_translations,
            # relations
            phasemetadata_id=objectivemetadata.phasemetadata_id,
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


exportMetadataCrud = CRUDObjectiveMetadata(ObjectiveMetadata)


class CRUDObjective(CRUDBase[Objective, ObjectiveCreate, ObjectivePatch]):
    def create_from_metadata(self, db: Session, objectivemetadata: ObjectiveMetadata, phase_id: uuid.UUID, language: str) -> Optional[Objective]:
        clone = row2dict(objectivemetadata)
        clone["name"] = objectivemetadata.name_translations[language]
        clone["description"] = objectivemetadata.description_translations[language]
        creator = ObjectiveCreate(**clone, phase_id=phase_id)
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
