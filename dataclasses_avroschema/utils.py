import typing
from dataclasses import dataclass
from datetime import datetime
import decimal
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


# This is an almost complete copy of fastavro's _logical_writers_py.prepare_bytes_decimal
# the only tweak is to pass in scale/precision directly instead of a schema
def prepare_bytes_decimal(data, precision, scale=0):
    """Convert decimal.Decimal to bytes"""
    # print(data, precision, scale)

    if not isinstance(data, decimal.Decimal):
        return data

    sign, digits, exp = data.as_tuple()

    if len(digits) > precision:
        raise ValueError(
            'The decimal precision is bigger than allowed by schema')

    delta = exp + scale

    if delta < 0:
        raise ValueError(
            'Scale provided in schema does not match the decimal')

    unscaled_datum = 0
    for digit in digits:
        unscaled_datum = (unscaled_datum * 10) + digit

    unscaled_datum = 10 ** delta * unscaled_datum

    bytes_req = (unscaled_datum.bit_length() + 8) // 8

    if sign:
        unscaled_datum = -unscaled_datum

    return unscaled_datum.to_bytes(bytes_req, byteorder='big', signed=True)

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
