from typing import Optional

from sqlalchemy.orm import Session

from app.general.utils.CRUDBase import CRUDBase
from app.models import Phase, PhaseMetadata, Status
from app.schemas import (
    PhaseCreate,
    PhasePatch,
    PhaseMetadataCreate,
    PhaseMetadataPatch,
    PhaseInternalPatch
)
import uuid
from app.general.utils.RowToDict import row2dict


class CRUDPhaseMetadata(CRUDBase[PhaseMetadata, PhaseMetadataCreate, PhaseMetadataPatch]):
    def create(self, db: Session, phasemetadata: PhaseMetadataCreate) -> PhaseMetadata:
        db_obj = PhaseMetadata(
            name_translations=phasemetadata.name_translations,
            description_translations=phasemetadata.description_translations,
            # relations
            coproductionschema_id=phasemetadata.coproductionschema_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_name(self, db: Session, name: str, language: str = "en") -> Optional[PhaseMetadata]:
        return db.query(PhaseMetadata).filter(PhaseMetadata.name_translations[language] == name).first()

    def add_prerequisite(self, db: Session, phasemetadata: PhaseMetadata, prerequisite: PhaseMetadata) -> PhaseMetadata:
        if phasemetadata.id == prerequisite.id:
            raise Exception("Same object")
        phasemetadata.prerequisites.append(prerequisite)
        db.commit()
        db.refresh(phasemetadata)
        return phasemetadata

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


exportMetadataCrud = CRUDPhaseMetadata(PhaseMetadata)

class CRUDPhase(CRUDBase[Phase, PhaseCreate, PhasePatch]):
    def create_from_metadata(self, db: Session, phasemetadata: PhaseMetadata, coproductionprocess_id: uuid.UUID, language: str) -> Optional[Phase]:
        clone = row2dict(phasemetadata)
        clone["name"] = phasemetadata.name_translations[language]
        clone["description"] = phasemetadata.description_translations[language]
        creator = PhaseCreate(**clone, coproductionprocess_id=coproductionprocess_id)
        return self.create(db=db, phase=creator)

    def get_by_name(self, db: Session, name: str) -> Optional[Phase]:
        return db.query(Phase).filter(Phase.name == name).first()

    def create(self, db: Session, *, phase: PhaseCreate) -> Phase:
        db_obj = Phase(
            name=phase.name,
            description=phase.description,
            # relations
            coproductionprocess_id=phase.coproductionprocess_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_prerequisite(self, db: Session, phase: Phase, prerequisite: Phase) -> Phase:
        if phase.id == prerequisite.id:
            raise Exception("Same object")
        phase.prerequisites.append(prerequisite)
        db.commit()
        db.refresh(phase)
        return phase

    def remove(self, db: Session, *, id: uuid.UUID) -> Phase:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        related = db.query(Phase).filter(Phase.prerequisites.any(Phase.id == obj.id)).all()
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


exportCrud = CRUDPhase(Phase)
