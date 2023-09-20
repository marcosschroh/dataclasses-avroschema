import datetime
import decimal
import typing

from .version import PY_VERSION

if PY_VERSION >= (3, 9):
    from typing import Annotated  # type: ignore
else:
    from typing_extensions import Annotated  # type: ignore # pragma: no cover

if PY_VERSION >= (3, 10):
    from types import UnionType  # type: ignore # pragma: no cover
else:
    UnionType = None  # type: ignore # pragma: no cover

T = typing.TypeVar("T")
JsonDict = typing.Dict[str, typing.Any]

# This represents how avro.type is represneted in json.
AvroTypeRepr = typing.Union[JsonDict, typing.List, str]


class FieldInfo:
    ...


class Fixed:
    ...


class DecimalFieldInfo(FieldInfo):
    def __init__(self, max_digits: int = -1, decimal_places: int = 0) -> None:
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def __repr__(self) -> str:
        return f"DecimalFieldInfo(max_digits={self.max_digits}, decimal_places={self.decimal_places})"


class FixedFieldInfo(FieldInfo):
    def __init__(
        self, size: int, aliases: typing.Optional[typing.List[str]] = None, namespace=typing.Optional[str]
    ) -> None:
        self.size = size
        self.aliases = aliases
        self.namespace = namespace

    def __repr__(self) -> str:
        return f"FixedFieldInfo(size={self.size}, aliases={self.aliases}, namespace={self.namespace})"


def confixed(
    *, size, aliases: typing.Optional[typing.List[str]] = None, namespace: typing.Optional[str] = None
) -> typing.Type[bytes]:
    return Annotated[  # type: ignore[return-value]
        Fixed, FixedFieldInfo(size=size, aliases=aliases, namespace=namespace)
    ]


def condecimal(*, max_digits: int, decimal_places: int) -> typing.Type[decimal.Decimal]:
    return Annotated[  # type: ignore[return-value]
        decimal.Decimal, DecimalFieldInfo(max_digits=max_digits, decimal_places=decimal_places)
    ]


Int32 = Annotated[int, "Int32"]
Float32 = Annotated[float, "Float32"]
TimeMicro = Annotated[datetime.time, "TimeMicro"]
DateTimeMicro = Annotated[datetime.datetime, "DateTimeMicro"]

CUSTOM_TYPES = (
    Int32,
    Float32,
    TimeMicro,
    DateTimeMicro,
    condecimal,
    confixed,
)
