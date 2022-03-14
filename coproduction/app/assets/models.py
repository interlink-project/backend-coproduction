import json
import uuid
from typing import TypedDict

import requests
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import orm
from sqlalchemy.sql.expression import null

from app.config import settings
from app.general.db.base_class import Base as BaseModel


class Asset(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_asset_id = Column(String)
    softwareinterlinker_id = Column(UUID(as_uuid=True))
    # save from which knowledge interlinker has been cloned, if so
    knowledgeinterlinker_id = Column(UUID(as_uuid=True), nullable=True)

    task_id = Column(
        UUID(as_uuid=True), ForeignKey("task.id", ondelete='SET NULL')
    )
    task = orm.relationship("Task", back_populates="assets")

    # also attach to the coproduction process to do not delete if task deleted
    coproductionprocess_id = Column(
        UUID(as_uuid=True), ForeignKey("coproductionprocess.id", ondelete='CASCADE')
    )
    coproductionprocess = orm.relationship(
        "CoproductionProcess", back_populates="assets")

    # created by
    creator_id = Column(
        String, ForeignKey("user.id")
    )
    creator = orm.relationship("User", back_populates="created_assets")

    def set_links(self):
        response = requests.get(
            f"http://{settings.CATALOGUE_SERVICE}/api/v1/interlinkers/{self.softwareinterlinker_id}").json()

        backend = response["backend"]
        self.ext_link = f"{backend}/{self.external_asset_id}"

        integration_data = response["integration"]
        backend = integration_data["service_name"]
        api_path = integration_data["api_path"]
        self.int_link = f"http://{backend}{api_path}/{self.external_asset_id}"
        self.caps = {
            "clone": integration_data["clone"],
            "view": integration_data["view"],
            "edit": integration_data["edit"],
            "delete": integration_data["delete"],
            "download": integration_data["download"],
        }
        self.interlinker_data = {
            "id": response["id"],
            "name": response["name"],
            "description": response["description"],
            "logotype_link": response["logotype_link"],
        }

    # on init
    @orm.reconstructor
    def init_on_load(self):
        self.set_links()

    def __repr__(self):
        return "<Asset %r>" % self.id

    @property
    def capabilities(self):
        return self.caps

    @property
    def link(self):
        return self.ext_link

    # not exposed in out schema
    @property
    def internal_link(self):
        return self.int_link
