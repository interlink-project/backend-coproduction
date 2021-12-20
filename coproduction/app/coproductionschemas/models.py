from typing import TypedDict

from app.general.db.base_class import Base as BaseModel
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.tables import coproductionschema_phase_association_table
import uuid

class CoproductionSchema(BaseModel):
    """
    Defines phase structure of a coproduction process
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_public = Column(Boolean)
    name = Column(String)
    description = Column(String)
    
    phases = relationship(
        "Phase",
        secondary=coproductionschema_phase_association_table,
        back_populates="schemas",
    )

    def __repr__(self):
        return "<CoproductionSchema %r>" % self.name