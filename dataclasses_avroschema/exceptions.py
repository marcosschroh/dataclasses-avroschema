import typing


class NameSpaceRequiredException(Exception):
    def __init__(self, field_type: typing.Any, field_name: str) -> None:
        self.field_type = field_type
        self.field_name = field_name

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name} {self.field_name},{self.field_type}"

    def __str__(self) -> str:
        return (  # pragma: no cover
            f"Required namespace in Meta for type {self.field_type}. "
            f"The field {self.field_name} is using an exiting type"
        )


class InvalidMap(Exception):
    def __init__(self, field_name: str, key_type: typing.Any) -> None:
        self.field_name = field_name
        self.key_type = key_type

    def __repr__(self) -> str:
        class_name = self.__class__.__name__  # pragma: no cover
        return f"{class_name} {self.field_name}"  # pragma: no cover

    def __str__(self) -> str:
        return f"Invalid map on field {self.field_name}. Keys must be string not {self.key_type}"
