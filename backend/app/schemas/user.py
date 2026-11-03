from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    department_id: Optional[int] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    role_names: List[str] = ["Employee"]

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    role_names: Optional[List[str]] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class UserRead(UserBase):
    id: int
    is_locked: bool
    roles: List[RoleRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead

class TokenRefreshRequest(BaseModel):
    refresh_token: str
