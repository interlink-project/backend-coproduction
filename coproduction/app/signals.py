
from sqlalchemy import event
from app.models import Permission, InternalAsset
from app.worker import sync_asset_users

@event.listens_for(Permission, "after_insert")
@event.listens_for(Permission, "after_update")
@event.listens_for(Permission, "after_delete")
def after_insert(mapper, connection, target: Permission):
    sync_asset_users.delay(target.treeitem_id)


@event.listens_for(InternalAsset, "after_insert")
@event.listens_for(InternalAsset, "after_update")
def after_insert(mapper, connection, target: InternalAsset):
    print("Asset created", target)


@event.listens_for(InternalAsset, "after_delete")
def after_insert(mapper, connection, target: InternalAsset):
    print("Asset deleted", target)
    # TODO: send post to interlinker to delete asset