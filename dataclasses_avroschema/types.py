import dataclasses
import datetime
import sys
import typing

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated  # type: ignore # pragma: no cover

if sys.version_info >= (3, 10):
    from types import UnionType  # pragma: no cover
else:
    UnionType = None  # pragma: no cover

T = typing.TypeVar("T")
JsonDict = typing.Dict[str, typing.Any]

CUSTOM_TYPES = (
    "Fixed",
    "Decimal",
    "Int32",
    "Float32",
    "TimeMicro",
    "DateTimeMicro",
)

__all__ = CUSTOM_TYPES


class FieldInfo:
    def __init__(self, **kwargs) -> None:
        self.type = kwargs.get("type")
        self.max_digits = kwargs.get("max_digits")
        self.decimal_places = kwargs.get("decimal_places")

    @property
    def metadata(self):
        return {
            "type": self.type,
            "max_digits": self.max_digits,
            "decimal_places": self.decimal_places,
        }


class MissingSentinel(typing.Generic[T]):
    """
    Class to detect when a field is not initialized
    """

    ...


@dataclasses.dataclass(frozen=True)
class Fixed(typing.Generic[T]):
    """
    Represents an Avro Fixed type

    size (int): Specifying the number of bytes per value
    """

    size: int
    default: typing.Any = dataclasses.field(default=MissingSentinel)
    namespace: typing.Optional[str] = None
    aliases: typing.Optional[typing.List] = None
    _dataclasses_custom_type: str = "Fixed"

    def __repr__(self) -> str:
        return f"{self.size}"


class Decimal:
    """
    Represents an Avro Decimal type
    precision (int): Specifying the number precision
    scale(int): Specifying the number scale. Default 0
    """

    def __init__(
        self,
        *,
        precision: int,
        scale: int = 0,
        default: typing.Any = MissingSentinel,
        aliases: typing.Optional[typing.List] = None,
    ) -> None:
        self.precision = precision
        self.scale = scale
        self.default = default
        self.aliases = aliases

    # Decimal serializes to bytes, which doesn't support namespace

    def __repr__(self) -> str:
        return f"Decimal('{self.default}')"


Int32 = Annotated[int, FieldInfo(type="Int32")]
Float32 = Annotated[float, FieldInfo(type="Float32")]
TimeMicro = Annotated[datetime.time, FieldInfo(type="TimeMicro")]
DateTimeMicro = Annotated[datetime.datetime, FieldInfo(type="DateTimeMicro")]
