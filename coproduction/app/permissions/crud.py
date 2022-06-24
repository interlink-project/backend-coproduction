from typing import List
from app import models, schemas
from app.general.utils.CRUDBase import CRUDBase
from app.models import Permission, TreeItem
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import or_

class CRUDPermission(CRUDBase[Permission, schemas.PermissionCreate, schemas.PermissionPatch]):
    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, treeitem: TreeItem
    ) -> List[Permission]:
        return db.query(Permission).filter(
            Permission.treeitem_id.in_(treeitem.path_ids)
        ).order_by(Permission.created_at.asc()).offset(skip).limit(limit).all()
    
    async def get_for_user_and_coproductionprocesss(
        self, db: Session, user: models.User, coproductionprocess_id: uuid.UUID
    ):
        return db.query(
                models.Permission
            ).filter(
                models.Permission.treeitem_id == models.TreeItem.id,
                models.Permission.coproductionprocess_id == coproductionprocess_id
            ).filter(
                or_(
                    models.Permission.user_id == user.id,
                    models.Permission.team_id.in_(user.teams_ids)
                )
            ).all()

    def enrich_log_data(self, obj, logData):
        logData["model"] = "PERMISSION"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.coproductionprocess_id
        logData["treeitem_id"] = obj.treeitem_id
        logData["team_id"] = obj.team_id
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
