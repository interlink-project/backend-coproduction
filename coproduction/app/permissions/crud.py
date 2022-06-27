import copy
import uuid
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.general.utils.CRUDBase import CRUDBase
from app.models import Permission, TreeItem
from app.permissions.models import DENY_ALL, PERMS


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
            Permission.treeitem_id.in_(treeitem.path_ids),
            Permission.coproductionprocess_id == treeitem.coproductionprocess.id,
            or_(
                Permission.user_id == user.id,
                Permission.team_id.in_(user.teams_ids)
            )
        ).all()

    def get_for_user_and_coproductionprocesss(
        self, db: Session, user: models.User, coproductionprocess_id: uuid.UUID
    ):
        return db.query(
            models.Permission
        ).filter(
            models.Permission.treeitem_id == models.TreeItem.id,
            models.Permission.coproductionprocess_id == coproductionprocess_id  # TODO: delete
        ).filter(
            or_(
                models.Permission.user_id == user.id,
                models.Permission.team_id.in_(user.teams_ids)
            )
        ).all()

    def get_user_roles(self, db: Session, treeitem: models.TreeItem, user: models.User):
        return [perm.team.type.value for perm in self.get_for_user_and_treeitem(db=db, user=user, treeitem=treeitem)]

    def get_dict_over_treeitem(self, db: Session, treeitem: models.TreeItem, user: models.User):
        permissions = self.get_for_user_and_treeitem(db=db, user=user, treeitem=treeitem)
        
        final_permissions_dict = copy.deepcopy(DENY_ALL)
        final_permissions_dict["access_assets_permission"] = True
        final_permissions_dict["delete_assets_permission"] = any(getattr(permission, "delete_assets_permission") for permission in permissions)
        final_permissions_dict["create_assets_permission"] = any(getattr(permission, "create_assets_permission") for permission in permissions)
        return final_permissions_dict

    def enrich_log_data(self, obj, logData, db, user):
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
            perms : dict = self.get_dict_over_treeitem(db=db, treeitem=task, user=user)
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
