import enum

class Permissions(enum.Enum):
    view_assets = "view_assets"
    create_assets = "create_assets"
    delete_assets = "delete_assets"
    change_access = "change_access"
    update_settings = "update_settings"


permissions_list = [e.value for e in Permissions]
