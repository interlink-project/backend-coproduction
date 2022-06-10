def recursive_check(id, obj):
    if hasattr(obj, "prerequisites"):
        for pre in obj.prerequisites:
            if id == pre.id:
                raise Exception("Circular prerequisite", id, obj.id)
            return recursive_check(id, pre)
    return