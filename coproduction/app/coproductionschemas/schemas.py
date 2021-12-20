import uuid
from datetime import datetime
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class CoproductionSchemaBase(BaseModel):
    name: str
    is_public: bool
    description: str

class CoproductionSchemaCreate(CoproductionSchemaBase):
    pass


class CoproductionSchemaPatch(CoproductionSchemaBase, metaclass=AllOptional):
    pass


class CoproductionSchema(CoproductionSchemaBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class CoproductionSchemaOut(CoproductionSchema):
    pass