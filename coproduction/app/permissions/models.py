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
    
    # for
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User', foreign_keys=[user_id], backref=backref('permissions', passive_deletes=True))
    team_id = Column(UUID(as_uuid=True), ForeignKey('team.id', ondelete='CASCADE'))
    team = relationship('Team', foreign_keys=[team_id], backref=backref('permissions', passive_deletes=True))
    
    # in
    coproductionprocess_id = Column(UUID(as_uuid=True), ForeignKey('coproductionprocess.id', ondelete='CASCADE'))
    coproductionprocess = relationship('CoproductionProcess', foreign_keys=[coproductionprocess_id], backref=backref('permissions', passive_deletes=True))
    treeitem_id = Column(UUID(as_uuid=True), ForeignKey('treeitem.id', ondelete='CASCADE'))
    treeitem = relationship('TreeItem', foreign_keys=[treeitem_id], backref=backref('permissions', passive_deletes=True))

    # to
    # create_treeitem_permission = Column(Boolean, default=False)
    edit_treeitem_permission = Column(Boolean, default=False)
    delete_treeitem_permission = Column(Boolean, default=False)
    view_assets_permission = Column(Boolean, default=False)
    create_assets_permission = Column(Boolean, default=False)
    delete_assets_permission = Column(Boolean, default=False)
    # IMPORTANT TO HAVE "_permission" STRING IN FIELD NAME for the classmethod

    def __repr__(self):
        return "<Permission>"

# DO NOT REMOVE
GRANT_ALL = {}
DENY_ALL = {}
PERMS = [field for field in dir(Permission) if "_permission" in field]
for perm in PERMS:
    GRANT_ALL[perm] = True
    DENY_ALL[perm] = False

"""
GRANT_ALL = {'create_assets_permission': True, 'delete_assets_permission': True, 'delete_treeitem_permission': True, 'edit_treeitem_permission': True, 'view_assets_permission': True} 
DENY_ALL = {'create_assets_permission': False, 'delete_assets_permission': False, 'delete_treeitem_permission': False, 'edit_treeitem_permission': False, 'view_assets_permission': False}
"""