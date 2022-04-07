import uuid
from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator
from typing_extensions import Annotated

from app.general.utils.AllOptional import AllOptional


class BaseAssetBase(BaseModel):
    task_id: Optional[uuid.UUID]
    coproductionprocess_id: Optional[uuid.UUID]

class BaseAssetCreate(BaseAssetBase):
    pass

class BaseAssetPatch(BaseAssetCreate, metaclass=AllOptional):
    pass


class BaseAsset(BaseAssetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class BaseAssetOut(BaseAssetBase):
    pass

# Internal asset

class InternalAssetBase(BaseAssetBase):
    type: Literal["internalasset"] = "internalasset"
    softwareinterlinker_id: uuid.UUID
    knowledgeinterlinker_id: Optional[uuid.UUID]
    external_asset_id: str
    
class InternalAssetCreate(BaseAssetCreate, InternalAssetBase):
    pass

class InternalAssetPatch(BaseAssetPatch, InternalAssetCreate, metaclass=AllOptional):
    pass


class InternalAsset(InternalAssetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    capabilities: Optional[dict]
    interlinker_data: dict
    
    class Config:
        orm_mode = True


class InternalAssetOut(BaseAssetOut, InternalAsset):
    link: str


# External asset

class ExternalAssetBase(BaseAssetBase):
    type: Literal["externalasset"] = "externalasset"
    externalinterlinker_id: uuid.UUID
    name: str
    uri: str
    
class ExternalAssetCreate(BaseAssetCreate, ExternalAssetBase):
    pass

class ExternalAssetPatch(BaseAssetPatch, ExternalAssetCreate, metaclass=AllOptional):
    pass


class ExternalAsset(ExternalAssetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class ExternalAssetOut(BaseAssetOut, ExternalAsset):
    pass



AssetCreate = Annotated[
    Union[ExternalAssetCreate, InternalAssetCreate],
    Field(discriminator="type"),
]

AssetPatch = Annotated[
    Union[ExternalAssetPatch, InternalAssetPatch],
    Field(discriminator="type"),
]


class AssetOut(BaseModel):
    __root__: Annotated[
        Union[ExternalAssetOut, InternalAssetOut],
        Field(discriminator="type"),
    ]
