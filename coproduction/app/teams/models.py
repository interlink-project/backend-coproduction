import uuid

from sqlalchemy import Column, ForeignKey, String, Table, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.general.db.base_class import Base as BaseModel
from app.config import settings
from app.users.models import User
from sqlalchemy.ext.associationproxy import association_proxy
from app.tables import user_team_association_table, team_role_association_table

class Team(BaseModel):
    """Team Class contains standard information for a Team."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    logotype = Column(String, nullable=True)

    # created by
    creator_id = Column(
        String, ForeignKey("user.id")
    )
    creator = relationship("User", back_populates="created_teams")

    users = relationship(
        "User",
        secondary=user_team_association_table,
        backref="teams")
    user_ids = association_proxy('users', 'id')

    roles = relationship(
        "Role",
        secondary=team_role_association_table,
        back_populates="teams")

    @property
    def logotype_link(self):
        return settings.COMPLETE_SERVER_NAME + self.logotype if self.logotype else ""
