import typing


class NameSpaceRequiredException(Exception):
    def __init__(self, field_type: typing.Any, field_name: str) -> None:
        self.field_type = field_type
        self.field_name = field_name

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name} {self.field_name},{self.field_type}"

    def __str__(self) -> str:
        return (
            f"Required namespace in Meta for type {self.field_type}. "
            f"The field {self.field_name} is using an exiting type"
        )
