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

    task_id = Column(
        UUID(as_uuid=True), ForeignKey("task.id", ondelete='CASCADE')
    )
    task = relationship("Task", back_populates="assets")

    # created by
    creator_id = Column(
        String, ForeignKey("user.id")
    )
    creator = relationship("User", back_populates="created_assets")

    def __repr__(self):
        return "<Asset %r>" % self.id
    
    @property
    def link(self):
        response = requests.get(f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/{self.interlinker_id}").json()
        backend = response["backend"]
        return f"{backend}/{self.external_id}"