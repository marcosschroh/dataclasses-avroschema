import datetime
import typing

from dataclasses_avroschema import field_utils

from . import templates
from .base_class import BaseClassEnum

_AVRO_TYPE_TO_PYTHON: typing.Dict[str, str] = {
    field_utils.BOOLEAN: "bool",
    field_utils.LONG: "int",
    field_utils.DOUBLE: "float",
    field_utils.BYTES: "bytes",
    field_utils.STRING: "str",
    field_utils.INT: "types.Int32",
    field_utils.FLOAT: "types.Float32",
    field_utils.DECIMAL: "decimal.Decimal",
    field_utils.DATE: "datetime.date",
    field_utils.TIME_MILLIS: "datetime.time",
    field_utils.TIME_MICROS: "types.TimeMicro",
    field_utils.TIMESTAMP_MILLIS: "datetime.datetime",
    field_utils.TIMESTAMP_MICROS: "types.DateTimeMicro",
    field_utils.UUID: "uuid.UUID",
}

AVRO_TYPE_TO_PYTHON: typing.Dict[str, typing.Dict[str, str]] = {
    BaseClassEnum.AVRO_MODEL.value: _AVRO_TYPE_TO_PYTHON,
    BaseClassEnum.PYDANTIC_MODEL.value: {
        **_AVRO_TYPE_TO_PYTHON,
        field_utils.UUID: "pydantic.UUID4",
    },
    BaseClassEnum.AVRO_DANTIC_MODEL.value: {
        **_AVRO_TYPE_TO_PYTHON,
        field_utils.UUID: "pydantic.UUID4",
    },
}

_LOGICAL_TYPES_IMPORTS: typing.Dict[str, str] = {
    field_utils.DECIMAL: "import decimal",
    field_utils.DATE: "import datetime",
    field_utils.TIME_MILLIS: "import datetime",
    field_utils.TIME_MICROS: "from dataclasses_avroschema import types",
    field_utils.TIMESTAMP_MILLIS: "import datetime",
    field_utils.TIMESTAMP_MICROS: "from dataclasses_avroschema import types",
    field_utils.UUID: "import uuid",
}
LOGICAL_TYPES_IMPORTS: typing.Dict[str, typing.Dict[str, str]] = {
    BaseClassEnum.AVRO_MODEL.value: _LOGICAL_TYPES_IMPORTS,
    BaseClassEnum.PYDANTIC_MODEL.value: {
        **_LOGICAL_TYPES_IMPORTS,
        field_utils.UUID: "import pydantic",
    },
    BaseClassEnum.AVRO_DANTIC_MODEL.value: {
        **_LOGICAL_TYPES_IMPORTS,
        field_utils.UUID: "import pydantic",
    },
}

# Avro types to python types
LOGICAL_TYPES_TO_PYTHON = {
    field_utils.DATE: lambda value: datetime.date.fromtimestamp(60 * 60 * 24 * value),
    field_utils.TIME_MILLIS: lambda value: (datetime.datetime.min + datetime.timedelta(milliseconds=value)).time(),
    field_utils.TIME_MICROS: lambda value: (datetime.datetime.min + datetime.timedelta(microseconds=value)).time(),
    field_utils.TIMESTAMP_MILLIS: lambda value: datetime.datetime.fromtimestamp(value / 1000),
    field_utils.TIMESTAMP_MICROS: lambda value: datetime.datetime.fromtimestamp(value / 1000000),
}

# Logical types objects to template
LOGICAL_TYPE_TEMPLATES = {
    field_utils.DATE: lambda date_obj: templates.date_template.safe_substitute(
        year=date_obj.year, month=date_obj.month, day=date_obj.day
    ),
    field_utils.TIME_MILLIS: lambda time_obj: templates.time_template.safe_substitute(
        hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second
    ),
    field_utils.TIME_MICROS: lambda time_obj: templates.time_micros_template.safe_substitute(
        hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second, microsecond=time_obj.microsecond
    ),
    field_utils.TIMESTAMP_MILLIS: lambda datetime_obj: templates.datetime_template.safe_substitute(
        year=datetime_obj.year,
        month=datetime_obj.month,
        day=datetime_obj.day,
        hour=datetime_obj.hour,
        minute=datetime_obj.minute,
        second=datetime_obj.second,
    ),
    field_utils.TIMESTAMP_MICROS: lambda datetime_obj: templates.datetime_micros_template.safe_substitute(
        year=datetime_obj.year,
        month=datetime_obj.month,
        day=datetime_obj.day,
        hour=datetime_obj.hour,
        minute=datetime_obj.minute,
        second=datetime_obj.second,
        microsecond=datetime_obj.microsecond,
    ),
}


def render_datetime(*, value: int, format: str) -> str:
    fn = LOGICAL_TYPES_TO_PYTHON[format]
    datetime_obj = fn(value)

    template = LOGICAL_TYPE_TEMPLATES[format]
    return template(datetime_obj)
