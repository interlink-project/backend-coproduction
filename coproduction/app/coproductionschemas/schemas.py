import uuid
from datetime import datetime
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class CoproductionSchemaBase(BaseModel):
    is_public: bool
    licence: str
    author: str

class CoproductionSchemaCreate(CoproductionSchemaBase):
    name_translations: dict
    description_translations: dict


class CoproductionSchemaPatch(CoproductionSchemaBase, metaclass=AllOptional):
    pass


class CoproductionSchema(CoproductionSchemaBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    name: str
    description: str
    class Config:
        orm_mode = True


class CoproductionSchemaOut(CoproductionSchema):
    pass