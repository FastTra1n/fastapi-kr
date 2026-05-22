from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional

class StatusType(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str]
    status: StatusType
    priority: int = Field(..., ge=1, lt=5)

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    owner_id: int

class TaskStatusUpdate(BaseModel):
    status: StatusType
