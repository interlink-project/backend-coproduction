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
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import association_proxy

from app.config import settings
from app.general.db.base_class import Base as BaseModel
from cached_property import cached_property


class AssetsData(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    