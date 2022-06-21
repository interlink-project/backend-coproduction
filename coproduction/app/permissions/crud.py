from typing import List
from app import models, schemas
from app.general.utils.CRUDBase import CRUDBase
from app.models import Permission, TreeItem
import uuid
from sqlalchemy.orm import Session

class CRUDPermission(CRUDBase[Permission, schemas.PermissionCreate, schemas.PermissionPatch]):
    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, treeitem: TreeItem
    ) -> List[Permission]:
        return db.query(Permission).filter(
            Permission.treeitem_id.in_(treeitem.path_ids)
        ).order_by(Permission.created_at.asc()).offset(skip).limit(limit).all()
    
    def enrich_log_data(self, obj, logData):
        logData["model"] = "PERMISSION"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.coproductionprocess_id
        logData["treeitem_id"] = obj.treeitem_id
        logData["roles"] = obj.treeitem.user_roles
        return logData

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
