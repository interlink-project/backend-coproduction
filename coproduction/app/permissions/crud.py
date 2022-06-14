from app import models, schemas
from app.general.utils.CRUDBase import CRUDBase
from app.models import Permission

class CRUDPermission(CRUDBase[Permission, schemas.PermissionCreate, schemas.PermissionPatch]):
    def enrich_log_data(self, obj, logData):
        logData["model"] = "PERMISSION"
        logData["object_id"] = obj.id
        logData["coproductionprocess_id"] = obj.coproductionprocess_id
        logData["treeitem_id"] = obj.treeitem_id
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
