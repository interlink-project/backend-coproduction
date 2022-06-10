import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    Enum
)
from sqlalchemy.dialects.postgresql import UUID
from app.general.db.base_class import Base as BaseModel
from app.config import settings
from app.tables import organization_administrators_association_table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref, relationship

class OrganizationTypes(enum.Enum):
    citizen = "citizen"
    public_office = "public_office"
    nonprofit_organization = "nonprofit_organization"
    forprofit_organization = "forprofit_organization"

class Organization(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(OrganizationTypes, create_constraint=False, native_enum=False), nullable=False)

    name = Column(String)
    description = Column(String)
    logotype = Column(String, nullable=True)

    administrators = relationship(
        "User",
        secondary=organization_administrators_association_table,
        backref="administrated_organizations")
    administrators_ids = association_proxy('administrators', 'id')

    @property
    def logotype_link(self):
        return settings.COMPLETE_SERVER_NAME + self.logotype if self.logotype else ""
