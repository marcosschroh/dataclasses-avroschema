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


class FieldValueError(ValueError):
    def __init__(
        self,
        field_name: str,
        field_type: typing.Type[typing.Any],
        field_value: typing.Any,
    ) -> None:
        self.field_name = field_name
        self.field_type = field_type
        self.field_value = field_value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__  # pragma: no cover
        return f"{class_name} {self.field_name}"  # pragma: no cover

    def __str__(self) -> str:
        return f'Invalid value "{self.field_value}" assigned to field "{self.field_name}" of type {self.field_type}'
