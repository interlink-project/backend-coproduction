import uuid
from datetime import datetime
from typing import List, Optional

from app.general.utils.AllOptional import AllOptional
from pydantic import BaseModel

class TaskBase(BaseModel):
    name: str
    is_public: bool
    description: str
    objective_id: uuid.UUID

class TaskCreate(TaskBase):
    pass


class TaskPatch(TaskBase, metaclass=AllOptional):
    pass


class Task(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class TaskOut(Task):
    pass

####

class TaskInstantiationBase(BaseModel):
    task_id: uuid.UUID
    objectiveinstantiation_id: uuid.UUID

class TaskInstantiationCreate(TaskInstantiationBase):
    pass


class TaskInstantiationPatch(TaskInstantiationBase, metaclass=AllOptional):
    pass


class TaskInstantiation(TaskInstantiationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class TaskInstantiationOut(TaskInstantiation):
    task: TaskOut
    name: str
    description: str
    recommended_interlinkers: Optional[List[uuid.UUID]]
