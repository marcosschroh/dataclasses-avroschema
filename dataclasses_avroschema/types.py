import dataclasses
import datetime
import decimal
import sys
import typing

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated  # pragma: no cover

if sys.version_info >= (3, 10):
    from types import UnionType  # pragma: no cover
else:
    UnionType = None  # pragma: no cover

T = typing.TypeVar("T")
JsonDict = typing.Dict[str, typing.Any]


class FieldInfo:
    def __init__(self, type: str, max_digits: int = -1, decimal_places: int = 0) -> None:
        self.type = type
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def __repr__(self) -> str:
        return f"FieldInfo(type='{self.type}', max_digits={self.max_digits}, decimal_places={self.decimal_places})"


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


def condecimal(*, max_digits: int, decimal_places: int) -> typing.Type[decimal.Decimal]:
    return Annotated[  # type: ignore[return-value]
        decimal.Decimal, FieldInfo(type="Decimal", max_digits=max_digits, decimal_places=decimal_places)
    ]


Int32 = Annotated[int, "Int32"]
Float32 = Annotated[float, "Float32"]
TimeMicro = Annotated[datetime.time, "TimeMicro"]
DateTimeMicro = Annotated[datetime.datetime, "DateTimeMicro"]

CUSTOM_TYPES = (
    Fixed,
    Int32,
    Float32,
    TimeMicro,
    DateTimeMicro,
    condecimal,
)
