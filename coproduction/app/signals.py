
from sqlalchemy import event
from app.models import Permission, InternalAsset, User, TreeItem
from app.worker import sync_asset_users, sync_asset_treeitems
import requests
from app.config import settings
from app.sockets import socket_manager

@event.listens_for(User, "after_update")
@event.listens_for(User, "after_delete")
def after_user_update_or_delete(mapper, connection, target: User):
    sync_asset_users.delay([target.id])

@event.listens_for(Permission, "after_insert")
@event.listens_for(Permission, "after_update")
@event.listens_for(Permission, "after_delete")
async def after_permission_insert_update_or_delete(mapper, connection, target: Permission):
    sync_asset_treeitems.delay([target.treeitem_id])
    await socket_manager.send_to_id(target.coproductionprocess_id, {
        "event": "PERMISSION_INSERT_UPDATE_DELETE"
    })

@event.listens_for(InternalAsset, "after_insert")
@event.listens_for(InternalAsset, "after_update")
async def after_asset_insert_or_update(mapper, connection, target: InternalAsset):
    print("Asset created", target)
    sync_asset_treeitems.delay([target.task_id])


@event.listens_for(InternalAsset, "after_delete")
async def after_asset_delete(mapper, connection, target: InternalAsset):
    print("Asset deleted", target)
    URL = target.internal_link
    requests.delete(URL, headers={
        "Authorization": settings.BACKEND_SECRET
    })

@event.listens_for(InternalAsset, "after_insert")
@event.listens_for(InternalAsset, "after_update")
@event.listens_for(InternalAsset, "after_delete")
async def after_asset_insert_or_update(mapper, connection, target: InternalAsset):
    await socket_manager.send_to_id(target.coproductionprocess_id, {
        "event": "ASSET_INSERT_UPDATE"
    })

@event.listens_for(TreeItem, "after_insert")
@event.listens_for(TreeItem, "after_update")
@event.listens_for(TreeItem, "after_delete")
async def after_treeitem_insert_or_update(mapper, connection, target: TreeItem):
    await socket_manager.send_to_id(target.coproductionprocess_id, {
        "event": "TREEITEM_INSERT_UPDATE_DELETE"
    })