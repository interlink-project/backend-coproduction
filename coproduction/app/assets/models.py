import json
import uuid
from typing import TypedDict

import requests
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null

from app.config import settings
from app.general.db.base_class import Base as BaseModel


class Asset(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String)
    interlinker_id = Column(UUID(as_uuid=True))

    taskinstantiation_id = Column(
        UUID(as_uuid=True), ForeignKey("taskinstantiation.id", ondelete='CASCADE')
    )
    taskinstantiation = relationship("TaskInstantiation", back_populates="assets")

    def __repr__(self):
        return "<Asset %r>" % self.id
    
    @property
    def file_metadata(self):
        response = requests.get(f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/{self.interlinker_id}")
        interlinker = response.json()
        backend = interlinker["backend"]
        response = requests.get(f"http://{backend}/api/v1/assets/{self.external_id}")
        return response.json()