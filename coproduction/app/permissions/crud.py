import copy
import uuid
from typing import List

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app import models, schemas
from app.general.utils.CRUDBase import CRUDBase
from app.models import Permission, TreeItem
from app.permissions.models import DENY_ALL, PERMS, GRANT_ALL, INDEXES


class CRUDPermission(CRUDBase[Permission, schemas.PermissionCreate, schemas.PermissionPatch]):
    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, treeitem: TreeItem
    ) -> List[Permission]:
        return db.query(Permission).filter(
            Permission.treeitem_id.in_(treeitem.path_ids)
        ).order_by(Permission.created_at.asc()).offset(skip).limit(limit).all()

    def get_for_user_and_treeitem(
        self, db: Session, user: models.User, treeitem: models.TreeItem
    ):
        return db.query(
            Permission
        ).filter(
            or_(
                and_(
                    Permission.treeitem_id.in_(treeitem.path_ids),
                    Permission.coproductionprocess_id == treeitem.coproductionprocess.id
                ),
                and_(
                    Permission.treeitem_id == None,
                    Permission.coproductionprocess_id == treeitem.coproductionprocess.id
                ),
            ),
            Permission.team_id.in_(user.teams_ids)
        ).all()

    def get_user_roles(self, db: Session, treeitem: models.TreeItem, user: models.User):
        roles = []
        for perm in self.get_for_user_and_treeitem(db=db, user=user, treeitem=treeitem):
            role = perm.team.type.value
            if role not in roles:
                roles.append(role)

        if user in treeitem.coproductionprocess.administrators:
            roles.append('administrator')
        return roles

    def get_dict_for_user_and_treeitem(self, db: Session, treeitem: models.TreeItem, user: models.User):
        if user in treeitem.coproductionprocess.administrators:
            return GRANT_ALL
        permissions = self.get_for_user_and_treeitem(db=db, user=user, treeitem=treeitem)

        final_permissions_dict = copy.deepcopy(DENY_ALL)
        indexes_dict = copy.deepcopy(INDEXES)
        
        path = treeitem.path_ids
        
        for permission in permissions:
            path_con = permission.treeitem_id or permission.coproductionprocess_id
            index = path.index(path_con)
            
            for permission_key in PERMS:
                if index > indexes_dict[permission_key]:
                    final_permissions_dict[permission_key] = getattr(permission, permission_key)
                    indexes_dict[permission_key] = index
                elif index == indexes_dict[permission_key] and not final_permissions_dict[permission_key] and getattr(permission, permission_key):
                    final_permissions_dict[permission_key]  = True

        return final_permissions_dict

    def enrich_log_data(self, obj, logData):
        logData["model"] = "PERMISSION"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.coproductionprocess_id
        logData["treeitem_id"] = obj.treeitem_id
        logData["team_id"] = obj.team_id
        return logData

    def user_can(self, db, user, task, permission):
        if user in task.coproductionprocess.administrators:
            return True
        if permission in PERMS:
            perms : dict = self.get_dict_for_user_and_treeitem(db=db, treeitem=task, user=user)
            return perms[permission]
        raise Exception(permission + " is not a valid permission")

    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def can_read(self, user, object):
        return True

    def can_update(self, user, object):
        return True

    def can_remove(self, user, object):
        return True


exportCrud = CRUDPermission(Permission, logByDefault=True)
