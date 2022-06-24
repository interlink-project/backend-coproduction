import copy
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Table, or_, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Session, relationship

from app.general.db.base_class import Base as BaseModel
from app.permissions.models import Permission, GRANT_ALL, DENY_ALL, PERMS
from app.utils import cached_hybrid_property, Status

prerequisites = Table(
    'treeitem_prerequisites', BaseModel.metadata,
    Column('treeitem_a_id', ForeignKey(
        'treeitem.id', ondelete="CASCADE"), primary_key=True),
    Column('treeitem_b_id', ForeignKey(
        'treeitem.id', ondelete="CASCADE"), primary_key=True)
)



class TreeItem(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(70))
    name = Column(String)
    description = Column(String)

    # prerequisites
    prerequisites = relationship("TreeItem", secondary=prerequisites,
                                 primaryjoin=id == prerequisites.c.treeitem_a_id,
                                 secondaryjoin=id == prerequisites.c.treeitem_b_id,
                                 )

    prerequisites_ids = association_proxy('prerequisites', 'id')

    # created by
    creator_id = Column(String, ForeignKey(
        "user.id", use_alter=True, ondelete='SET NULL'))
    creator = relationship('User', foreign_keys=[
                           creator_id], post_update=True, backref="created_treeitems")

    # state
    status = Column(Enum(Status, create_constraint=False,
                    native_enum=False), default=Status.awaiting)

    # Disabled by
    disabler_id = Column(String, ForeignKey(
        "user.id", use_alter=True, ondelete='SET NULL'))
    disabler = relationship('User', foreign_keys=[
                            disabler_id], post_update=True, backref="disabled_treeitems")
    disabled_on = Column(DateTime)

    from_item = Column(UUID(as_uuid=True))
    from_schema = Column(UUID(as_uuid=True))

    teams = association_proxy('_permissions', 'team')

    __mapper_args__ = {
        "polymorphic_identity": "treeitem",
        "polymorphic_on": type,
    }

    @cached_hybrid_property
    def permissions(self):
        db = Session.object_session(self)
        # Get permissions of the treeitem for user (and teams he or she belongs to)...
        return db.query(
            Permission
        ).filter(
            Permission.treeitem_id.in_(self.path_ids)
        ).all()

    @cached_hybrid_property
    def user_roles(self):
        from app.general.deps import get_current_user_from_context
        db = Session.object_session(self)

        roles = []
        if user := get_current_user_from_context(db=db):
            roles = [perm.team.type.value for perm in self.user_permissions]
            if user in self.coproductionprocess.administrators:
                roles.append("administrator")
        return roles

    @cached_hybrid_property
    def user_permissions(self):
        from app.general.deps import get_current_user_from_context
        db = Session.object_session(self)
        if user := get_current_user_from_context(db=db):

            # Get permissions of the treeitem for user (and teams he or she belongs to)...
            return db.query(
                Permission
            ).filter(
                Permission.treeitem_id.in_(self.path_ids),
                or_(
                    Permission.user_id == user.id,
                    Permission.team_id.in_(user.teams_ids)
                )
            ).all()
        return []

    @cached_hybrid_property
    def user_permissions_dict(self):
        from app.general.deps import get_current_user_from_context

        db = Session.object_session(self)
        if user := get_current_user_from_context(db=db):
            # If admin, grant all
            print("llega", GRANT_ALL)
            if user in self.coproductionprocess.administrators:
                return GRANT_ALL
            # And check if any of the permission has the flag of the permission key as True
            final_permissions_dict = copy.deepcopy(DENY_ALL)
            # final_permissions_dict["access_assets_permission"] = True
            for permission_key in PERMS:
                final_permissions_dict[permission_key] = any(getattr(permission, permission_key) for permission in self.user_permissions)
            return final_permissions_dict
        return DENY_ALL

    def user_can(self, permission: str):
        if permission in PERMS:
            return self.user_permissions_dict[permission]
        raise Exception(permission + " is not a valid permission")
