from typing import Any, Dict, List, Optional, Type, TypeVar, Union, ClassVar, Callable, Generic, Sequence, overload

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
_T = TypeVar("_T")

class MetaData:
    pass

class Column:
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

class ForeignKey:
    def __init__(self, column: str, **kwargs: Any) -> None: ...

class Table:
    pass

class relationship:
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

# SQLAlchemy типы данных
class TypeEngine:
    pass

class String(TypeEngine):
    def __init__(self, length: Optional[int] = None, **kwargs: Any) -> None: ...

class Integer(TypeEngine):
    pass

class Float(TypeEngine):
    pass

class Boolean(TypeEngine):
    pass

class DateTime(TypeEngine):
    def __init__(self, timezone: bool = False, **kwargs: Any) -> None: ...

class Text(TypeEngine):
    pass

class Enum:
    def __init__(self, *enums: Any, **kwargs: Any) -> None: ...

# Функции SQLAlchemy
class func:
    @classmethod
    def now(cls) -> Any: ...
    
    @classmethod
    def current_timestamp(cls) -> Any: ...

class DeclarativeMeta(type):
    metadata: ClassVar[MetaData]
    __tablename__: ClassVar[str]
    __table__: ClassVar[Table]

    def __init__(self) -> None: ...
    def __init_subclass__(cls, **kwargs: Any) -> None: ...

class Engine:
    def connect(self) -> Any: ...
    def raw_connection(self) -> Any: ...
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...

class Session:
    def add(self, instance: Any) -> None: ...
    def add_all(self, instances: List[Any]) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...
    def query(self, entity: Type[T], *entities: Any) -> Query[T]: ...
    def flush(self) -> None: ...

class Query(Generic[T_co]):
    def filter(self, *criteria: Any) -> 'Query[T_co]': ...
    def filter_by(self, **kwargs: Any) -> 'Query[T_co]': ...
    def all(self) -> List[T_co]: ...
    def first(self) -> Optional[T_co]: ...
    def one(self) -> T_co: ...
    def one_or_none(self) -> Optional[T_co]: ...
    def scalar(self) -> Optional[Any]: ...
    def count(self) -> int: ... 