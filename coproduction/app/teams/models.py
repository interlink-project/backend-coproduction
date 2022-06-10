import uuid

from sqlalchemy import Column, ForeignKey, String, Table, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.general.db.base_class import Base as BaseModel
from app.config import settings
from app.users.models import User
from sqlalchemy.ext.associationproxy import association_proxy
from app.tables import user_team_association_table
from app.organizations.models import OrganizationTypes
from app.tables import team_administrators_association_table

class Team(BaseModel):
    """Team Class contains standard information for a Team."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    logotype = Column(String, nullable=True)

    # created by
    creator_id = Column(String, ForeignKey("user.id", use_alter=True, ondelete='SET NULL'))
    creator = relationship('User', foreign_keys=[creator_id], post_update=True, back_populates="created_teams")

    # in case of being nonprofit of profit organization
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organization.id', ondelete='CASCADE'))
    organization = relationship('Organization', foreign_keys=[organization_id], backref=backref('roles', passive_deletes=True))

    users = relationship(
        "User",
        secondary=user_team_association_table,
        backref="teams")
    user_ids = association_proxy('users', 'id')

    administrators = relationship(
        "User",
        secondary=team_administrators_association_table,
        backref="administrated_teams")
    administrators_ids = association_proxy('administrators', 'id')

    @property
    def logotype_link(self):
        return settings.COMPLETE_SERVER_NAME + self.logotype if self.logotype else ""

    @property
    def type(self):
        if self.organization:
            return self.organization.type
        return OrganizationTypes.citizen