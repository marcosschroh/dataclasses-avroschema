import datetime
import decimal
import typing
from typing import Annotated

T = typing.TypeVar("T")
JsonDict = typing.Dict[str, typing.Any]

# This represents how avro.type is represneted in json.
AvroTypeRepr = typing.Union[JsonDict, typing.List, str]
SerializationType = typing.Literal["avro", "avro-json"]


class FieldInfo: ...


class Fixed: ...


class DecimalFieldInfo(FieldInfo):
    def __init__(self, max_digits: int = -1, decimal_places: int = 0) -> None:
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def __repr__(self) -> str:
        return f"DecimalFieldInfo(max_digits={self.max_digits}, decimal_places={self.decimal_places})"


class FixedFieldInfo(FieldInfo):
    def __init__(
        self,
        size: int,
        aliases: typing.Optional[typing.List[str]] = None,
        namespace=typing.Optional[str],
    ) -> None:
        self.size = size
        self.aliases = aliases
        self.namespace = namespace

    def __repr__(self) -> str:
        return f"FixedFieldInfo(size={self.size}, aliases={self.aliases}, namespace={self.namespace})"


class Int32FieldInfo(FieldInfo): ...


class Float32FieldInfo(FieldInfo): ...


class TimeMicroFieldInfo(FieldInfo): ...


class DateTimeMicro2FieldInfo(FieldInfo): ...


def confixed(
    *,
    size,
    aliases: typing.Optional[typing.List[str]] = None,
    namespace: typing.Optional[str] = None,
) -> typing.Type[bytes]:
    return Annotated[Fixed, FixedFieldInfo(size=size, aliases=aliases, namespace=namespace)]  # type: ignore[return-value]


def condecimal(*, max_digits: int, decimal_places: int) -> typing.Type[decimal.Decimal]:
    return Annotated[
        decimal.Decimal,
        DecimalFieldInfo(max_digits=max_digits, decimal_places=decimal_places),
    ]  # type: ignore[return-value]


Int32 = Annotated[int, Int32FieldInfo()]
Float32 = Annotated[float, Float32FieldInfo()]
TimeMicro = Annotated[datetime.time, TimeMicroFieldInfo()]
DateTimeMicro = Annotated[datetime.datetime, DateTimeMicro2FieldInfo()]

CUSTOM_TYPES = (
    Int32,
    Float32,
    TimeMicro,
    DateTimeMicro,
    condecimal,
    confixed,
)
