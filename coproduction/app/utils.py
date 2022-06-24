from sqlalchemy.ext.hybrid import hybrid_property
import enum

def recursive_check(id, obj):
    if hasattr(obj, "prerequisites"):
        for pre in obj.prerequisites:
            if id == pre.id:
                raise Exception("Circular prerequisite", id, obj.id)
            return recursive_check(id, pre)
    return

# https://stackoverflow.com/questions/34057756/how-to-combine-sqlalchemys-hybrid-property-decorator-with-werkzeugs-cached-pr

_missing = object()   # sentinel object for missing values

class cached_hybrid_property(hybrid_property):
    def __get__(self, instance, owner):
        if instance is None:
            # getting the property for the class
            return self.expr(owner)
        else:
            # getting the property for an instance
            name = self.fget.__name__
            value = instance.__dict__.get(name, _missing)
            if value is _missing:
                value = self.fget(instance)
                instance.__dict__[name] = value
            return value

class Status(str, enum.Enum):
    awaiting = "awaiting"
    in_progress = "in_progress"
    finished = "finished"

class RoleTypes(str, enum.Enum):
    citizen = "citizen"
    public_administration = "public_administration"
    nonprofit_organization = "nonprofit_organization"
    forprofit_organization = "forprofit_organization"

class ActionTypes(str, enum.Enum):
    create_administrator = "create_administrator"
    remove_administrator = "remove_administrator"
    add_user_to_team = "add_user_to_team"
    remove_user_from_team = "remove_user_from_team"
    create_instance = "create_instance"
    delete_instance = "delete_instance"
    disable_instance = "disable_instance"

class ModelTypes(str, enum.Enum):
    COPRODUCTIONPROCESS = "CoproductionProcess"
    ORGANIZATION = "Organization"
    TEAM = "Team"
    ASSET = "Asset"
    TREEITEM = "TreeItem"

def update_status_and_progress(treeitem):
    statuses = [child.status for child in getattr(treeitem, "children") if not getattr(child, "disabled_on")]
    status = Status.awaiting
    if all([x == Status.finished for x in statuses]):
        status = Status.finished
    elif all([x == Status.awaiting for x in statuses]):
        status = Status.awaiting
    else:
        status = Status.in_progress
    countInProgress = statuses.count(Status.in_progress) / 2
    countFinished = statuses.count(Status.finished)
    length = len(statuses)
    progress = int((countInProgress + countFinished) * 100 / length) if length > 0 else 0
    setattr(treeitem, "status", status)
    setattr(treeitem, "progress", progress)
    return treeitem