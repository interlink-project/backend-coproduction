from sqlalchemy import (
    Column
)
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.general.db.base_class import Base as BaseModel
from app.tables import coproductionprocess_tags_association_table
from app.locales import translation_hybrid


class Tag(BaseModel):
    """
    Defines the tag model
    """
    id = Column(UUID(as_uuid=True), primary_key=True)
    name_translations = Column(HSTORE)
    description_translations = Column(HSTORE)

    name = translation_hybrid(name_translations)
    description = translation_hybrid(description_translations)


    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
