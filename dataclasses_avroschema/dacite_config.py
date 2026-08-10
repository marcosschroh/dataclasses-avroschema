import enum
import typing
import uuid
from datetime import date, datetime, time

from dacite import Config
from dateutil import parser

if typing.TYPE_CHECKING:
    from .main import AvroModel  # pragma: no cover


DateTimeParseType = typing.Union[str, datetime]
DateParseType = typing.Union[str, date]
TimeParseType = typing.Union[str, time]
BytesParseType = typing.Union[str, bytes]
UUIDParseType = typing.Union[str, uuid.UUID]

# `dateutil.parser.parse` takes free-form text, and the cost of its tokenizer grows faster
# than the length of the string it is handed: measured on this parser, doubling the input
# multiplies the time by about 3.3. A timestamp needs a small fraction of this, so longer
# values are refused before the parser sees them. Raise it if a project needs to accept
# longer text, or pass a different hook through `Meta.dacite_config`.
MAX_DATETIME_STRING_LENGTH = 256


def parse_timestamp(value: str) -> datetime:
    """Parse a timestamp of a bounded length."""
    if len(value) > MAX_DATETIME_STRING_LENGTH:
        raise ValueError(
            f"The value is {len(value)} characters long, above the maximum of "
            f"{MAX_DATETIME_STRING_LENGTH} (`dacite_config.MAX_DATETIME_STRING_LENGTH`)"
        )

    return parser.parse(value)


def parse_datetime(value: DateTimeParseType) -> DateTimeParseType:
    if isinstance(value, str):
        return parse_timestamp(value)
    return value


def parse_date(value: DateParseType) -> DateParseType:
    if isinstance(value, str):
        dt = parse_timestamp(value)
        return dt.date()
    return value


def parse_time(value: TimeParseType) -> TimeParseType:
    if isinstance(value, str):
        dt = parse_timestamp(value)
        return dt.time()
    return value


def parse_bytes(value: BytesParseType) -> BytesParseType:
    if isinstance(value, str):
        return value.encode()
    return value


def parse_uuid(value: UUIDParseType) -> UUIDParseType:
    if isinstance(value, str):
        return uuid.UUID(value)
    return value


def generate_dacite_config(model: typing.Type["AvroModel"]) -> Config:
    """
    Get the default config for dacite and always include the self reference
    """
    # We need to make sure that the `avro schemas` has been generated, otherwise cls._dataclass is empty
    # It won't affect the performance because the rendered schema will be store in model._rendered_schema
    model.generate_schema()
    dacite_user_config = model._parser.metadata.dacite_config  # type: ignore

    dacite_config = {
        "check_types": False,
        "cast": [],
        "forward_references": {
            model._parser.dataclass.__name__: model._parser.dataclass,  # type: ignore
        },
        "type_hooks": {
            datetime: parse_datetime,
            date: parse_date,
            time: parse_time,
            bytes: parse_bytes,
            uuid.UUID: parse_uuid,
        },
    }

    if dacite_user_config is not None:
        dacite_config.update(dacite_user_config)

    config = Config(**dacite_config)  # type: ignore

    # we always need to have this values regardless
    # the user config
    config.cast.extend([typing.Tuple, tuple, enum.Enum])  # type: ignore
    return config
