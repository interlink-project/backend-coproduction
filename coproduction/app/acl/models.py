from ast import Str
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
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from sqlalchemy_utils import ChoiceType

from app.config import settings
from app.general.db.base_class import Base as BaseModel

ACTIONS = {"create": "create", "update": "update",
           "retrieve": "retrieve", "delete": "delete"}

def DEFAULT_ACTIONS():
    return ["retrieve"]

DEFAULT_ROLES = [
    {
        "name": "admin",
        "permissions": list(ACTIONS.keys())
    },
    {
        "name": "reader",
        "permissions": DEFAULT_ACTIONS()
    },
    {
        "name": "unauthenticated",
        "permissions": []
    }
]


class ACL(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = relationship(
        "CoproductionProcess", back_populates="acl")

    roles = relationship(
        "Role", back_populates="acl")
    exceptions = relationship(
        "Exception", back_populates="acl")

    def __repr__(self):
        return "<Acl %r>" % self.id


class Role(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    permissions = Column(
        ARRAY(ChoiceType(ACTIONS)), default=DEFAULT_ACTIONS
    )
    exceptions = relationship(
        "Exception", back_populates="role")

    acl_id = Column(
        UUID(as_uuid=True), ForeignKey("acl.id", ondelete='CASCADE')
    )
    acl = relationship("ACL", back_populates="roles")

    def __repr__(self):
        return "<Role %r>" % self.name


class Exception(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    asset_id = Column(
        UUID(as_uuid=True), ForeignKey("asset.id", ondelete='CASCADE')
    )
    asset = relationship("Asset", backref="exceptions")

    acl_id = Column(
        UUID(as_uuid=True), ForeignKey("acl.id", ondelete='CASCADE')
    )
    acl = relationship("ACL", back_populates="exceptions")

    role_id = Column(
        UUID(as_uuid=True), ForeignKey("role.id", ondelete='CASCADE')
    )
    role = relationship("Role", back_populates="exceptions")

    permission = Column(ChoiceType(ACTIONS))
    grant = Column(Boolean)

    def __repr__(self):
        return "<Exception %r>" % self.id
