import uuid
from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator
from typing_extensions import Annotated


class AssetsDataBase(BaseModel):
    id: uuid.UUID
    name: str
    


class AssetsData(AssetsDataBase):
    
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True

class AssetsDataOut(AssetsData):
    pass
    
class AssetsDataPatch(AssetsDataBase):
    pass

class AssetsDataCreate(AssetsDataBase):
    pass


