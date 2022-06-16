import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    Enum,
    Boolean,
    func,
    Integer,
    ForeignKey

)
from sqlalchemy.dialects.postgresql import UUID, HSTORE
from app.general.db.base_class import Base as BaseModel
from app.config import settings
from app.tables import organization_administrators_association_table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from app.locales import translation_hybrid
from sqlalchemy_utils import aggregated
from sqlalchemy.orm import Session

class OrganizationTypes(str, enum.Enum):
    citizen = "citizen"
    public_office = "public_office"
    nonprofit_organization = "nonprofit_organization"
    forprofit_organization = "forprofit_organization"

class TeamCreationPermissions(str, enum.Enum):
    administrators = "administrators"
    members = "members"
    anyone = "anyone"

class Organization(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(OrganizationTypes, create_constraint=False, native_enum=False), nullable=False)

    public = Column(Boolean, default=False)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE, nullable=True)
    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)
    icon = Column(String, nullable=True)
    logotype = Column(String, nullable=True)
    
    creator_id = Column(String, ForeignKey(
        "user.id", use_alter=True, ondelete='SET NULL'))
    creator = relationship('User', foreign_keys=[creator_id], post_update=True, backref="created_organizations")

    administrators = relationship(
        "User",
        secondary=organization_administrators_association_table,
        backref="administrated_organizations")
    administrators_ids = association_proxy('administrators', 'id')

    team_creation_permission = Column(Enum(TeamCreationPermissions, create_constraint=False, native_enum=False), server_default=TeamCreationPermissions.administrators.value)

    teams_ids = association_proxy('teams', 'id')
    @property
    def icon_link(self):
        return settings.COMPLETE_SERVER_NAME + self.icon if self.icon else ""

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
            for team in self.teams:
                if user in team.users:
                    participations.append("member")
                    break
        return participations

    @property
    def people_involved(self):
        from app.models import User, Team
        db = Session.object_session(self)
        return db.query(User).distinct(User.id).join(
            Team
        ).filter(
            Team.organization_id == self.id
        ).count()