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
    namespace: str = None
    aliases: typing.List = None

    def __repr__(self):
        return f"{self.size}"


@dataclasses.dataclass
class Enum(typing.Generic[T]):
    """
    Represents an Avro Enum type

    simbols (typing.List): Specifying the possible values for the enum
    """

    symbols: typing.List[typing.Any]
    default: typing.Any = None
    namespace: str = None
    aliases: typing.List = None
    docs: str = None

    def __repr__(self):
        return f"{self.symbols}"
