from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Общие свойства
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Свойства для создания пользователя
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str


# Свойства для обновления пользователя
class UserUpdate(UserBase):
    password: Optional[str] = None


# Свойства, хранящиеся в БД
class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Свойства, возвращаемые клиенту
class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 