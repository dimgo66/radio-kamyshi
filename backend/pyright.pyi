from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy import MetaData
from pydantic import EmailStr

T = TypeVar('T')

# Расширение типов для Base
class SQLAlchemyBase:
    metadata: MetaData
    __tablename__: str
    __table__: Any
    
# Расширение типов для Settings
class SettingsType:
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str 