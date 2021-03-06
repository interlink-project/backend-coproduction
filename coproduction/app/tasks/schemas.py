from enum import Enum
import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from app.treeitems.schemas import *

class TaskCreate(TreeItemCreate):
    objective_id: Optional[uuid.UUID]
    problemprofiles: list
    status: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]

class TaskPatch(TreeItemPatch):
    problemprofiles: Optional[list]
    status: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]

class Task(TreeItem, TaskCreate):
    class Config:
        orm_mode = True


class TaskOut(Task, TreeItemOut):
    phase_id: uuid.UUID