import typing
from dataclasses import dataclass
from datetime import datetime

from pytz import utc

from .types import CUSTOM_TYPES


def is_union(a_type: typing.Any) -> bool:
    """
    Given a python type, return True if is typing.Union, otherwise False

    Arguments:
        a_type (typing.Any): python type

    Returns:
        bool
    """
    return isinstance(a_type, typing._GenericAlias) and a_type.__origin__ is typing.Union  # type: ignore


def is_self_referenced(a_type: typing.Any) -> bool:
    """
    Given a python type, return True if is self referenced, meaning
    that is instance of typing.ForwardRef, otherwise False

    Arguments:
        a_type (typing.Any): python type

    Returns:
        bool

    Example:
        a_type = typing.Type["User"]]

        is_self_referenced(a_type) # True
    """
    return (
        isinstance(a_type, typing._GenericAlias)  # type: ignore
        and a_type.__args__
        and isinstance(a_type.__args__[0], typing.ForwardRef)  # type: ignore
    )


def is_custom_type(value: typing.Any) -> bool:
    """
    Given a type, return True if is a custom type (Fixed, Enum)
    """
    return isinstance(value, dict) and value.get("_dataclasses_custom_type") in CUSTOM_TYPES


@dataclass
class SchemaMetadata:
    schema_doc: bool = True
    namespace: typing.Optional[typing.List[str]] = None
    aliases: typing.Optional[typing.List[str]] = None

    @classmethod
    def create(cls, klass: typing.Any) -> typing.Any:
        return cls(
            schema_doc=getattr(klass, "schema_doc", True),
            namespace=getattr(klass, "namespace", None),
            aliases=getattr(klass, "aliases", None),
        )


epoch: datetime = datetime(1970, 1, 1, tzinfo=utc)
epoch_naive: datetime = datetime(1970, 1, 1)
