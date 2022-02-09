import uuid
from datetime import datetime

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
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import relationship

from app.extern import acl
from app.general.db.base_class import Base as BaseModel
from app.general.utils.DatabaseLocalization import translation_hybrid


class CoproductionProcess(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE, nullable=True)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)

    logotype = Column(String, nullable=True)
    created_by = Column(String, nullable=False)

    aim = Column(Text, nullable=True)
    idea = Column(Text, nullable=True)
    organization = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)

    phases = relationship(
        "Phase", back_populates="coproductionprocess")
    roles = relationship("Role", back_populates="coproductionprocess")
    artefact_id = Column(UUID(as_uuid=True))

    # created from schema
    coproductionschema_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionschema.id")
    )
    coproductionschema = relationship("CoproductionSchema", back_populates="coproductionprocesses")

    # worked by
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("team.id")
    )
    team = relationship("Team", back_populates="coproductionprocesses")

    acl_id = Column(Text)

    def current_user_permissions(self, role):
        return acl.get_permissions_for_role(self.acl_id, role=role)
