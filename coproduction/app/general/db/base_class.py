from typing import Union, Dict as DictStrAny, Any, AbstractSet as AbstractSetIntStr, Mapping as MappingIntStrAny
import sqlalchemy
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr, as_declarative
import uuid

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @declared_attr
    def created_at(self):
        return Column(DateTime, server_default=func.now())

    @declared_attr
    def updated_at(self):
        return Column(DateTime, onupdate=func.now())

    # https://stackoverflow.com/questions/63264888/pydantic-using-property-getter-decorator-for-a-field-with-an-alias
    # Allow pydantic to serialize model properties
    @classmethod
    def get_properties(cls):
        return [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property) and prop not in ("__values__", "fields")]

    def dict(
        self,
        *,
        include: Union[AbstractSetIntStr, MappingIntStrAny] = None,
        exclude: Union[AbstractSetIntStr, MappingIntStrAny] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> DictStrAny:
        # Get all column properties (i.e., the SQLAlchemy model's fields)
        columns = [column.key for column in sqlalchemy.inspect(self.__class__).attrs if isinstance(column, sqlalchemy.orm.ColumnProperty)]

        # Construct a dictionary of column keys and their values
        attribs = {column: getattr(self, column) for column in columns}

        # ... (keep the rest of your code here for handling properties)
        
        props = self.get_properties()
        # Include and exclude properties
        if include:
            props = [prop for prop in props if prop in include]
        if exclude:
            props = [prop for prop in props if prop not in exclude]

        # Update the attribute dict with the properties
        if props:
            attribs.update({prop: getattr(self, prop) for prop in props})

        # Convert UUID objects to strings
        for key, value in attribs.items():
            if isinstance(value, uuid.UUID):
                attribs[key] = str(value)

        return attribs