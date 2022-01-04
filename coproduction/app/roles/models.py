import uuid
from datetime import datetime

from app.general.db.base_class import Base as BaseModel
from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, HSTORE
from sqlalchemy.orm import relationship
import uuid
from app.general.utils.DatabaseLocalization import translation_hybrid

class Role(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Text)
    role = Column(Text)
    coproductionprocess = relationship("CoproductionProcess")
    coproductionprocess_id = Column(UUID(as_uuid=True), ForeignKey("coproductionprocess.id"))
    user_id = Column(Text)
