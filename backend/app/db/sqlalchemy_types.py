"""
SQLAlchemy типы для подсказок типов в Pylance/Pyright
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, ClassVar, Callable, Generic, Sequence, overload
import sys

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)

@runtime_checkable
class SQLAlchemyBase(Protocol):
    """Протокол для классов SQLAlchemy Base."""
    __tablename__: str
    id: Any

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None: ...

# Определение типов для моделей SQLAlchemy
class SQLAColumnType:
    """Базовый тип для SQLAlchemy Column типов."""
    pass

# Типы SQLAlchemy колонок
class Integer(SQLAColumnType):
    """Integer тип SQLAlchemy."""
    pass

class String(SQLAColumnType):
    """String тип SQLAlchemy."""
    def __init__(self, length: Optional[int] = None, **kwargs: Any) -> None: ...

class Text(SQLAColumnType):
    """Text тип SQLAlchemy."""
    pass

class Boolean(SQLAColumnType):
    """Boolean тип SQLAlchemy."""
    pass

class DateTime(SQLAColumnType):
    """DateTime тип SQLAlchemy."""
    def __init__(self, timezone: bool = False, **kwargs: Any) -> None: ...

class Float(SQLAColumnType):
    """Float тип SQLAlchemy."""
    pass

class ForeignKey:
    """ForeignKey SQLAlchemy."""
    def __init__(self, column: str, **kwargs: Any) -> None: ...

class Column:
    """Column SQLAlchemy."""
    def __init__(
        self, 
        type_: Any = None, 
        *args: Any,
        primary_key: bool = False,
        nullable: bool = True,
        unique: bool = False,
        default: Any = None,
        index: bool = False,
        name: Optional[str] = None,
        onupdate: Any = None,
        server_default: Any = None,
        **kwargs: Any
    ) -> None: ...

class relationship:
    """relationship SQLAlchemy."""
    def __init__(
        self,
        argument: Union[Type[Any], str],
        secondary: Optional[Any] = None,
        primaryjoin: Optional[Any] = None,
        secondaryjoin: Optional[Any] = None,
        foreign_keys: Optional[Sequence[Column]] = None,
        uselist: Optional[bool] = None,
        order_by: Optional[Any] = None,
        backref: Optional[Union[str, Any]] = None,
        back_populates: Optional[str] = None,
        overlaps: Optional[str] = None,
        post_update: bool = False,
        cascade: Optional[str] = None,
        viewonly: bool = False,
        **kwargs: Any
    ) -> None: ...

class func:
    """Функции SQL."""
    
    @staticmethod
    def now() -> Any: ...
    
    @staticmethod
    def current_timestamp() -> Any: ...

# Определение для Enum
class Enum:
    """Enum для SQLAlchemy."""
    def __init__(self, *enums: Any, **kwargs: Any) -> None: ... 