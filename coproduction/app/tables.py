from app.general.db.base_class import Base as BaseModel
from sqlalchemy import Table, ForeignKey, Column

coproductionschema_phase_association_table = Table(
    "coproductionschema_phase",
    BaseModel.metadata,
    Column("coproductionschema_id", ForeignKey("coproductionschema.id")),
    Column("phase_id", ForeignKey("phase.id")),
)