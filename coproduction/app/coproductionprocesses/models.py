import uuid
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy import (
    ARRAY,
    Enum,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func
)
from sqlalchemy_utils import aggregated
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import relationship, object_session
from app import models
from app.general.db.base_class import Base as BaseModel
from app.config import settings
from app.roles.models import Role

class CoproductionProcess(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    language = Column(String, default=settings.DEFAULT_LANGUAGE)
    name = Column(String)
    description = Column(String)

    logotype = Column(String, nullable=True)
    aim = Column(Text, nullable=True)
    idea = Column(Text, nullable=True)
    organization = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)

    # created by
    creator_id = Column(String, ForeignKey("user.id", use_alter=True, ondelete='SET NULL'))
    creator = relationship('User', foreign_keys=[creator_id], post_update=True, back_populates="created_coproductionprocesses")

    default_role_id = Column(UUID(as_uuid=True), ForeignKey('role.id', use_alter=True, ondelete='SET NULL'))
    default_role = relationship('Role', foreign_keys=[default_role_id], post_update=True)

    @property
    def logotype_link(self):
        return settings.COMPLETE_SERVER_NAME + self.logotype if self.logotype else ""