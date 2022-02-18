import uuid
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

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
from sqlalchemy.dialects.postgresql import HSTORE, UUID
from sqlalchemy.orm import relationship, object_session
from app import models
from app.general.db.base_class import Base as BaseModel
from app.general.utils.DatabaseLocalization import translation_hybrid

association_table = Table('association_team_process', BaseModel.metadata,
                          Column('team_id', ForeignKey('team.id'), primary_key=True),
                          Column('coproductionprocess_id', ForeignKey('coproductionprocess.id'), primary_key=True))
                  
class CoproductionProcess(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String)
    description = Column(String)

    logotype = Column(String, nullable=True)
    aim = Column(Text, nullable=True)
    idea = Column(Text, nullable=True)
    organization = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)

    phases = relationship(
        "Phase", back_populates="coproductionprocess")
    artefact_id = Column(UUID(as_uuid=True))

    # created by
    creator_id = Column(
        String, ForeignKey("user.id")
    )
    creator = relationship("User", back_populates="created_coproductionprocesses")

    # worked by
    teams = relationship("Team", secondary=association_table, back_populates="coproductionprocesses")

    # ACL
    acl = relationship("ACL", back_populates="coproductionprocess", uselist=False)

    @property
    def acl_id(self):
        return self.acl.id
    
    @hybrid_property
    def phases_count(self):
        return object_session(self).query(models.Phase).filter(models.Phase.coproductionprocess_id==self.id).count()