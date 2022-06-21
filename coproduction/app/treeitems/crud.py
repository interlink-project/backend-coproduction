import uuid
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import TreeItem, User, Permission

class CRUDTreeItem:
    async def get(self, db: Session, id: uuid.UUID) -> Optional[TreeItem]:
        return db.query(TreeItem).filter(TreeItem.id == id).first()

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TreeItem]:
        return db.query(TreeItem).order_by(TreeItem.created_at.asc()).offset(skip).limit(limit).all()
    
    """
    async def roles_of_user_for_treeitem(
        self, db: Session, user: User, treeitem: TreeItem, all_permissions: list = None
    ):
        if not all_permissions:
            all_permissions = self.all_permissions_for_treeitem(user, treeitem)

        roles = [perm.team.type.value for perm in all_permissions]
        if user in treeitem.coproductionprocess.administrators:
            roles.append("administrator")
        return roles
    
    async def all_permissions_for_treeitem(
        self, db: Session, user: User, treeitem: TreeItem
    ):
        # Gets all the permissions for a given user for a treeitem (and its parents)
        return db.query(
                Permission
            ).filter(
                Permission.treeitem_id.in_(treeitem.path_ids),
                or_(
                    Permission.user_id == user.id,
                    Permission.team_id.in_(user.teams_ids)
                )
            ).all()

    def user_permissions_dict(self):
        if user in self.coproductionprocess.administrators:
                return GRANT_ALL
            # And check if any of the permission has the flag of the permission key as True
            final_permissions_dict = copy.deepcopy(DENY_ALL)
            for permission_key in PERMS:
                final_permissions_dict[permission_key] = any(getattr(permission, permission_key) for permission in self.user_permissions)
            return final_permissions_dict
        return DENY_ALL

    """

exportCrud = CRUDTreeItem()
