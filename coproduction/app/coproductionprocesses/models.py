import uuid
from datetime import datetime

from app.general.db.base_class import Base as BaseModel
from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, HSTORE
from sqlalchemy.orm import relationship
import uuid

from app.general.utils.DatabaseLocalization import translation_hybrid


class CoproductionProcess(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE, nullable=True)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)

    logotype = Column(Text, nullable=True)
    aim = Column(Text, nullable=True)
    idea = Column(Text, nullable=True)
    organization = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)

    phaseinstantiations = relationship("PhaseInstantiation", back_populates="coproductionprocess")
    
    artefact_id = Column(UUID(as_uuid=True))
    team_id = Column(UUID(as_uuid=True))

    @property
    def phaseinstantiations_ids(self):
        return [p.id for p in self.phaseinstantiations]