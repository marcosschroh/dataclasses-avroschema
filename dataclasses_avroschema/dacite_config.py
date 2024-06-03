import enum
import typing
import uuid
from datetime import date, datetime, time

from dacite import Config
from dateutil import parser

if typing.TYPE_CHECKING:
    from .schema_generator import AvroModel


DateTimeParseType = typing.Union[str, datetime]
DateParseType = typing.Union[str, date]
TimeParseType = typing.Union[str, time]
BytesParseType = typing.Union[str, bytes]
UUIDParseType = typing.Union[str, uuid.UUID]


def parse_datetime(value: DateTimeParseType) -> DateTimeParseType:
    if isinstance(value, str):
        return parser.parse(value)
    return value


def parse_date(value: DateParseType) -> DateParseType:
    if isinstance(value, str):
        dt = parser.parse(value)
        return dt.date()
    return value


def parse_time(value: TimeParseType) -> TimeParseType:
    if isinstance(value, str):
        dt = parser.parse(value)
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
    # We need to make sure that the `avro schemas` has been generated, otherwise cls._klass is empty
    # It won't affect the performance because the rendered schema will be store in model._rendered_schema
    model.generate_schema()
    dacite_user_config = model._metadata.dacite_config  # type: ignore

    dacite_config = {
        "check_types": False,
        "cast": [],
        "forward_references": {
            model._klass.__name__: model._klass,  # type: ignore
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
