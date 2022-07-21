
from sqlalchemy import event
from app.models import Permission, InternalAsset
from app.worker import sync_asset_users
import requests
from app.config import settings

@event.listens_for(Permission, "after_insert")
@event.listens_for(Permission, "after_update")
@event.listens_for(Permission, "after_delete")
def after_permission_insert_update_or_delete(mapper, connection, target: Permission):
    sync_asset_users.delay([target.treeitem_id])


@event.listens_for(InternalAsset, "after_insert")
@event.listens_for(InternalAsset, "after_update")
def after_asset_insert_or_update(mapper, connection, target: InternalAsset):
    print("Asset created", target)
    sync_asset_users.delay([target.task_id])


@event.listens_for(InternalAsset, "after_delete")
def after_asset_delete(mapper, connection, target: InternalAsset):
    print("Asset deleted", target)
    URL = target.internal_link
    requests.delete(URL, headers={
        "Authorization": settings.BACKEND_SECRET
    })
