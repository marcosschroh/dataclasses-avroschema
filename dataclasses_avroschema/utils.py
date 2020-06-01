import typing
from dataclasses import dataclass


def is_union(a_type: typing.Any) -> bool:
    """
    Given a python type, return True if is typing.Union, otherwise False

    Arguments:
        a_type (typing.Any): python type

    Returns:
        bool
    """
    return (
        isinstance(a_type, typing._GenericAlias)
        and a_type.__origin__  # type: ignore
        is typing.Union
    )


def is_self_referenced(a_type) -> bool:
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


@dataclass
class SchemaMetadata:
    schema_doc: bool = True
    namespace: typing.List[str] = None
    aliases: typing.List[str] = None

    @classmethod
    def create(cls, klass: typing.Any):
        return cls(
            schema_doc=getattr(klass, "schema_doc", True),
            namespace=getattr(klass, "namespace", None),
            aliases=getattr(klass, "aliases", None),
        )
