import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    Text,
    Boolean,
    func
)
from sqlalchemy_utils import aggregated
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.general.db.base_class import Base as BaseModel
from app.config import settings
from app.phases.models import Phase
from sqlalchemy.ext.associationproxy import association_proxy
from app.tables import coproductionprocess_administrators_association_table
from sqlalchemy.orm import Session

class CoproductionProcess(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schema_used = Column(UUID(as_uuid=True))
    language = Column(String, default=settings.DEFAULT_LANGUAGE)
    name = Column(String)
    description = Column(String)

    logotype = Column(String, nullable=True)
    aim = Column(Text, nullable=True)
    idea = Column(Text, nullable=True)
    organization = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)

    # created by
    creator_id = Column(String, ForeignKey(
        "user.id", use_alter=True, ondelete='SET NULL'))
    creator = relationship('User', foreign_keys=[
                           creator_id], post_update=True, backref="created_coproductionprocesses")
    administrators = relationship(
        "User",
        secondary=coproductionprocess_administrators_association_table,
        backref="administered_processes")
    administrators_ids = association_proxy('administrators', 'id')
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey(
        "organization.id", use_alter=True, ondelete='SET NULL'))
    organization = relationship('Organization', post_update=True, backref="coproductionprocesses")

    teams = association_proxy('permissions', 'team')

    @aggregated('children', Column(Date))
    def end_date(self):
        return func.max(Phase.end_date)

    @aggregated('children', Column(Date))
    def start_date(self):
        return func.min(Phase.start_date)

    @property
    def logotype_link(self):
        return settings.COMPLETE_SERVER_NAME + self.logotype if self.logotype else ""

    @property
    def user_participation(self):
        from app.general.deps import get_current_user_from_context
        db = Session.object_session(self)
        participations = []
        if user := get_current_user_from_context(db=db):
            if user in self.administrators:
                participations.append("administrator")
            else:
                participations.append("collaborator")
        return participations