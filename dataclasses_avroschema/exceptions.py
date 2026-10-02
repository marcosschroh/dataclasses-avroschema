import typing


class InvalidMap(Exception):
    def __init__(self, field_name: str, key_type: typing.Any) -> None:
        self.field_name = field_name
        self.key_type = key_type

    def __repr__(self) -> str:
        class_name = self.__class__.__name__  # pragma: no cover
        return f"{class_name} {self.field_name}"  # pragma: no cover

    def __str__(self) -> str:
        return f"Invalid map on field {self.field_name}. Keys must be string not {self.key_type}"


class InvalidSchemaValue(Exception):
    """
    A value taken from the schema cannot be rendered into the generated source.

    It is raised for the values that end up in code rather than in a string literal --
    a name, a namespace, an annotation -- where escaping does not apply and the only
    safe answer is to refuse the schema.
    """

    def __init__(self, value: typing.Any, location: str, expected: str) -> None:
        self.value = value
        self.location = location
        self.expected = expected

    def __repr__(self) -> str:
        class_name = self.__class__.__name__  # pragma: no cover
        return f"{class_name} {self.location}"  # pragma: no cover

    def __str__(self) -> str:
        return (
            f"Invalid {self.location} {self.value!r}. It is rendered into the generated source as code, "
            f"so it must be {self.expected}"
        )


class InvalidSymbol(Exception):
    def __init__(self, field_name: str, symbol: str) -> None:
        self.field_name = field_name
        self.symbol = symbol

    def __repr__(self) -> str:
        class_name = self.__class__.__name__  # pragma: no cover
        return f"{class_name} {self.field_name}"  # pragma: no cover

    def __str__(self) -> str:
        return f"Symbol {self.symbol} does not match the regular expression [A-Za-z_][A-Za-z0-9_]*"
