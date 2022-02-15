import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import object_session, relationship, backref

from app.general.db.base_class import Base as BaseModel
from app.memberships.models import Membership
from app.teams.models import Team
from app import schemas

association_table = Table('association_membership_role', BaseModel.metadata,
                          Column('membership_id', ForeignKey('membership.id'), primary_key=True),
                          Column('role_id', ForeignKey('role.id'), primary_key=True))

class Permissions(enum.Enum):
    assets_create = "assets_create"
    assets_update = "assets_update"
    assets_delete = "assets_delete"
    acl_update = "acl_update"
    process_update = "process_update"


permissions_list = [e.value for e in Permissions]


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
        ARRAY(Enum(Permissions, create_constraint=False, native_enum=False))
    )
    acl_id = Column(UUID(as_uuid=True), ForeignKey('acl.id'))
    acl = relationship('ACL', foreign_keys=[acl_id], back_populates='roles')

    memberships = relationship(
        "Membership",
        secondary=association_table,
        backref="roles")

    @property
    def membership_ids(self):
        return [membership.id for membership in self.memberships]

    def __repr__(self):
        return "<Role %r>" % self.name

class ACL(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = relationship(
        "CoproductionProcess", back_populates="acl")

    roles = relationship('Role', foreign_keys=[Role.acl_id], back_populates='acl')

    default_role_id = Column(UUID(as_uuid=True), ForeignKey('role.id', ondelete='SET NULL'))
    default_role = relationship('Role', foreign_keys=[default_role_id], post_update=True)

    def __repr__(self):
        return "<Acl %r>" % self.id

    @property
    def permissions(self):
        return permissions_list

    """@property
    def teams(self):
       ids = [role.id for role in self.roles]
        return object_session(self).query(Team).join(
            Team, Membership.team
        ).filter(
            Membership.roles.any(Role.id.in_(ids))
        ).all()"""


class Exception(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    asset_id = Column(
        UUID(as_uuid=True), ForeignKey("asset.id", ondelete='CASCADE')
    )
    asset = relationship("Asset", backref="exceptions")

    acl_id = Column(
        UUID(as_uuid=True), ForeignKey("acl.id", ondelete='CASCADE')
    )
    acl = relationship("ACL", backref="exceptions")

    role_id = Column(
        UUID(as_uuid=True), ForeignKey("role.id", ondelete='CASCADE')
    )
    role = relationship("Role", backref="exceptions")

    permission = Column(Enum(Permissions, create_constraint=False, native_enum=False))
    grant = Column(Boolean)

    def __repr__(self):
        return "<Exception %r>" % self.id