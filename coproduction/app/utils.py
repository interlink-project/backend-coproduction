from sqlalchemy.ext.hybrid import hybrid_property

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