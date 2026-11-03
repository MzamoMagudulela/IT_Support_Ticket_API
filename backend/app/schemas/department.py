from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DepartmentBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    manager_name: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    manager_name: Optional[str] = None

class DepartmentRead(DepartmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
