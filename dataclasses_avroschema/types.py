import dataclasses
import typing

T = typing.TypeVar("T")


@dataclasses.dataclass
class Fixed(typing.Generic[T]):
    """
    Represents an Avro Fixed type

    size (int): Specifying the number of bytes per value
    """

    size: int
    namespace: typing.Optional[str] = None
    aliases: typing.Optional[typing.List] = None
    _dataclasses_custom_type: str = "Fixed"

    def __repr__(self) -> str:
        return f"{self.size}"


@dataclasses.dataclass
class Enum(typing.Generic[T]):
    """
    Represents an Avro Enum type

    simbols (typing.List): Specifying the possible values for the enum
    """

    symbols: typing.List[typing.Any]
    default: typing.Optional[typing.Any] = None
    namespace: typing.Optional[str] = None
    aliases: typing.Optional[typing.List] = None
    docs: typing.Optional[str] = None
    _dataclasses_custom_type: str = "Enum"

    def __repr__(self) -> str:
        return f"{self.symbols}"


CUSTOM_TYPES = ("Fixed", "Enum")
