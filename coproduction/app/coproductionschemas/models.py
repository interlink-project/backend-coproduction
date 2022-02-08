import uuid
from sqlalchemy import (
    Boolean,
    Column,
    String
)
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import relationship

from app.general.db.base_class import Base as BaseModel
from app.tables import coproductionschema_phase_association_table
from app.translations import translation_hybrid


class CoproductionSchema(BaseModel):
    """
    Defines phase structure of a coproduction process
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)
    author = Column(String, nullable=True)
    licence = Column(String, nullable=True)

    phases = relationship(
        "Phase",
        secondary=coproductionschema_phase_association_table,
        back_populates="schemas",
    )

    def __repr__(self):
        return "<CoproductionSchema %r>" % self.name
