from email.policy import default
import uuid
from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Date,
    Text,
    Boolean,
    func
)
from sqlalchemy_utils import aggregated
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.general.db.base_class import Base as BaseModel
from app.config import settings
from app.phases.models import Phase
from sqlalchemy.ext.associationproxy import association_proxy
from app.tables import coproductionprocess_administrators_association_table, coproductionprocess_tags_association_table
from sqlalchemy.orm import Session
from app.utils import Status

class CoproductionProcess(BaseModel):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schema_used = Column(UUID(as_uuid=True))
    language = Column(String, default=settings.DEFAULT_LANGUAGE)
    name = Column(String)
    description = Column(String)

    logotype = Column(String, nullable=True)
    aim = Column(Text, nullable=True)
    idea = Column(Text, nullable=True)
    organization_desc = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)

    #Active Optional Modules
    incentive_and_rewards_state =Column(Boolean,nullable=True)
    is_part_of_publication = Column(Boolean,nullable=True)

    status = Column(Enum(Status, create_constraint=False,
                    native_enum=False), default=Status.in_progress)


    # created by
    creator_id = Column(String, ForeignKey(
        "user.id", use_alter=True, ondelete='SET NULL'))
    creator = relationship('User', foreign_keys=[
                           creator_id], post_update=True, backref="created_coproductionprocesses")
    administrators = relationship(
        "User",
        secondary=coproductionprocess_administrators_association_table,
        backref="administered_processes")
    administrators_ids = association_proxy('administrators', 'id')

    organization_id = Column(UUID(as_uuid=True), ForeignKey(
        "organization.id", use_alter=True, ondelete='SET NULL'))
    organization = relationship('Organization', post_update=True, backref="coproductionprocesses")

    teams = association_proxy('permissions', 'team')


    coproductionprocess_notification_associations = relationship(
        "CoproductionProcessNotification",
        back_populates="coproductionprocess",
        cascade="all, delete-orphan",
    )
    notifications = association_proxy("coproductionprocess_notification_associations", "notification")

    coproductionprocess_story_associations = relationship(
        "Story",
        back_populates="coproductionprocess",
        cascade="all, delete-orphan",
    )
    
    # Gamification
    game_id = Column(String, nullable=True)
    
    # Tags
    tags = relationship(
        'Tag',
        secondary=coproductionprocess_tags_association_table,
        backref='coproductionprocesses',
    )
    tags_ids = association_proxy('tags', 'id')
    
    
    stories = association_proxy("coproductionprocess_story_associations", "story")

    @aggregated('children', Column(Date))
    def end_date(self):
        return func.max(Phase.end_date)

    @aggregated('children', Column(Date))
    def start_date(self):
        return func.min(Phase.start_date)

    # the tree items can be disabled, so we need to retrieve only those teams or permissions that are not disabled
    @property
    def enabled_teams(self):
        return [perm.team for perm in self.permissions if not perm.treeitem or (perm.treeitem and not perm.treeitem.disabled_on)]
    
    @property
    def enabled_permissions(self):
        return [perm for perm in self.permissions if not perm.treeitem or (perm.treeitem and not perm.treeitem.disabled_on)]

    @property
    def logotype_link(self):
        return settings.COMPLETE_SERVER_NAME + self.logotype if self.logotype else ""

    @property
    def current_user_participation(self):
        from app.general.deps import get_current_user_from_context
        db = Session.object_session(self)
        participations = []
        if user := get_current_user_from_context(db=db):
            if user in self.administrators:
                participations.append("administrator")
            else:
                participations.append("collaborator")
        return participations

    def task_ids(self):
        res = []
        for phase in self.children:
            if not phase.disabled_on:
                for objective in phase.children:
                    if not objective.disabled_on:
                        for task in objective.children:
                            if not task.disabled_on:
                                res.append(task.id)
        return res