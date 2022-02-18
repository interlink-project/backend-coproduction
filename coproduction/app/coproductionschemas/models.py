import uuid
from sqlalchemy import (
    Boolean,
    Column,
    String,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import relationship, backref

from app.general.db.base_class import Base as BaseModel
from app.translations import translation_hybrid

class CoproductionSchema(BaseModel):
    """
    Defines phase structure of a coproduction process
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean, default=False)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    # TODO: supported languages
    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)
    author = Column(String, nullable=True)
    licence = Column(String, nullable=True)

    phasemetadatas = relationship("PhaseMetadata", back_populates="coproductionschema")

    def __repr__(self):
        return "<CoproductionSchema %r>" % self.name
