import typing

T = typing.TypeVar("T")


class Fixed(typing.Generic[T]):
    """
    Represents an Avro Fixed type

    size (int): Specifying the number of bytes per value
    """

    def __init__(
        self, size: int, namespace: str = None, aliases: typing.List = None
    ) -> None:
        self.size = size
        self.namespace = namespace
        self.aliases = aliases

    def __repr__(self):
        return f"{self.size}"
