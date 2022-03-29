import enum

class Permissions(enum.Enum):
    assets_view = "assets_view"
    assets_create = "assets_create"
    assets_update = "assets_update"
    assets_delete = "assets_delete"
    acl_update = "acl_update"
    process_update = "process_update"


permissions_list = [e.value for e in Permissions]
