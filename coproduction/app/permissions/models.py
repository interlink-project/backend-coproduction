import uuid
import enum
from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
from app.general.db.base_class import Base as BaseModel
from functools import lru_cache

class Permission(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # created by
    creator_id = Column(String, ForeignKey("user.id", use_alter=True, ondelete='SET NULL'))
    creator = relationship('User', foreign_keys=[creator_id], post_update=True, backref="created_permissions")

    # for (user not used yet)
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', foreign_keys=[user_id], backref=backref('permissions', passive_deletes=True))
    team_id = Column(UUID(as_uuid=True), ForeignKey('team.id', ondelete='CASCADE'))
    team = relationship('Team', foreign_keys=[team_id], backref=backref('permissions', passive_deletes=True))
    
    # in
    coproductionprocess_id = Column(UUID(as_uuid=True), ForeignKey('coproductionprocess.id', ondelete='CASCADE'))
    coproductionprocess = relationship('CoproductionProcess', foreign_keys=[coproductionprocess_id], backref=backref('permissions', passive_deletes=True))
    treeitem_id = Column(UUID(as_uuid=True), ForeignKey('treeitem.id', ondelete='CASCADE'))
    treeitem = relationship('TreeItem', foreign_keys=[treeitem_id], backref=backref('_permissions', passive_deletes=True))

    # to
    create_assets_permission = Column(Boolean, default=False)
    delete_assets_permission = Column(Boolean, default=False)
    # IMPORTANT TO HAVE "_permission" STRING IN FIELD NAME for the classmethod

    def __repr__(self):
        return "<Permission>"

# DO NOT REMOVE
GRANT_ALL = {'access_assets_permission': True}
DENY_ALL = {'access_assets_permission': False}

PERMS = [field for field in dir(Permission) if "_permission" in field] + ['access_assets_permission']
for perm in PERMS:
    GRANT_ALL[perm] = True
    DENY_ALL[perm] = False

"""
GRANT_ALL = {'create_assets_permission': True, 'delete_assets_permission': True, 'access_assets_permission': True} 
DENY_ALL = {'create_assets_permission': False, 'delete_assets_permission': False, 'access_assets_permission': False}
"""