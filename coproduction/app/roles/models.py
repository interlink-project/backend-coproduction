from email.policy import default
import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import backref, object_session, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from app import schemas
from app.general.db.base_class import Base as BaseModel
from app.teams.models import Team
from app.users.models import User
from app.permissions import Permissions, permissions_list
from app.tables import team_role_association_table, user_association_table

AdministratorRole = schemas.RoleBase(**{
    "name": "Administrator",
    "description": "Administrator rights for the project",
    "permissions": permissions_list
})

DefaultRole = schemas.RoleBase(**{
    "name": "Default",
    "description": "When users or teams added, these are the rights by default",
    "permissions": []
})

UnauthenticatedRole = schemas.RoleBase(**{
    "name": "Unauthenticated",
    "description": "Rights for unauthenticated users in case the process is public",
    "permissions": []
})


class Role(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    meta_editable = Column(Boolean, default=True)
    perms_editable = Column(Boolean, default=True)
    deletable = Column(Boolean, default=True)
    selectable = Column(Boolean, default=True)

    permissions = Column(
        ARRAY(Enum(Permissions, create_constraint=False, native_enum=False)), default=list
    )
    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey('coproductionprocess.id'))
    coproductionprocess = relationship('CoproductionProcess', foreign_keys=[
                                       coproductionprocess_id], back_populates='roles')

    users = relationship(
        "User",
        secondary=user_association_table,
        backref="roles")
    user_ids = association_proxy('users', 'id')

    teams = relationship(
        "Team",
        secondary=team_role_association_table,
        back_populates="roles")
    team_ids = association_proxy('teams', 'id')

    # @hybrid_property
    # def user_ids(self):
    #     return [user.id for user in self.users]

    # @hybrid_property
    # def team_ids(self):
    #     return [team.id for team in self.teams]

    def __repr__(self):
        return "<Role %r>" % self.name


class Exception(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    asset_id = Column(
        UUID(as_uuid=True), ForeignKey("asset.id", ondelete='CASCADE')
    )
    asset = relationship("Asset", backref="exceptions")

    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = relationship("CoproductionProcess", backref="exceptions")

    role_id = Column(
        UUID(as_uuid=True), ForeignKey("role.id", ondelete='CASCADE')
    )
    role = relationship("Role", backref="exceptions")

    permission = Column(Enum(Permissions, create_constraint=False, native_enum=False))
    grant = Column(Boolean)

    def __repr__(self):
        return "<Exception %r>" % self.id
