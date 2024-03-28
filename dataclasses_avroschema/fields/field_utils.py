import datetime
import enum
import uuid

from dataclasses_avroschema import types

__all__ = [
    "BOOLEAN",
    "NULL",
    "INT",
    "FLOAT",
    "LONG",
    "DOUBLE",
    "BYTES",
    "STRING",
    "ARRAY",
    "ENUM",
    "MAP",
    "FIXED",
    "DATE",
    "UUID",
    "DECIMAL",
    "RECORD",
    "TIME_MILLIS",
    "TIME_MICROS",
    "TIMESTAMP_MILLIS",
    "TIMESTAMP_MICROS",
    "LOGICAL_DATE",
    "LOGICAL_TIME_MILIS",
    "LOGICAL_TIME_MICROS",
    "LOGICAL_DATETIME_MILIS",
    "LOGICAL_DATETIME_MICROS",
    "LOGICAL_UUID",
    "PYTHON_TYPE_TO_AVRO",
]

TIME_MILLIS = "time-millis"
TIME_MICROS = "time-micros"
TIMESTAMP_MILLIS = "timestamp-millis"
TIMESTAMP_MICROS = "timestamp-micros"

BOOLEAN = "boolean"
NULL = "null"
INT = "int"
FLOAT = "float"
LONG = "long"
DOUBLE = "double"
BYTES = "bytes"
STRING = "string"
ARRAY = "array"
ENUM = "enum"
MAP = "map"
FIXED = "fixed"
DATE = "date"
UUID = "uuid"
DECIMAL = "decimal"
RECORD = "record"
LOGICAL_DATE = {"type": INT, "logicalType": DATE}
LOGICAL_TIME_MILIS = {"type": INT, "logicalType": TIME_MILLIS}
LOGICAL_TIME_MICROS = {"type": LONG, "logicalType": TIME_MICROS}
LOGICAL_DATETIME_MILIS = {"type": LONG, "logicalType": TIMESTAMP_MILLIS}
LOGICAL_DATETIME_MICROS = {"type": LONG, "logicalType": TIMESTAMP_MICROS}
LOGICAL_UUID = {"type": STRING, "logicalType": UUID}

AVRO_TYPES = (
    "boolean",
    "null",
    "int",
    "float",
    "long",
    "double",
    "bytes",
    "string",
    "array",
    "enum",
    "map",
    "fixed",
    "record",
)

PYTHON_TYPE_TO_AVRO = {
    bool: BOOLEAN,
    type(None): NULL,
    int: LONG,
    float: DOUBLE,
    bytes: BYTES,
    str: STRING,
    list: {"type": ARRAY},
    tuple: {"type": ARRAY},
    dict: {"type": MAP},
    enum.Enum: {"type": ENUM},
    types.Fixed: {"type": FIXED},
    types.Int32: INT,
    types.Float32: FLOAT,
    datetime.date: {"type": INT, "logicalType": DATE},
    datetime.time: {"type": INT, "logicalType": TIME_MILLIS},
    datetime.datetime: {"type": LONG, "logicalType": TIMESTAMP_MILLIS},
    uuid.uuid4: {"type": STRING, "logicalType": UUID},
}
