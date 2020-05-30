import datetime
import typing
import uuid

from dataclasses_avroschema import AvroModel, fields

now = datetime.datetime.now()

PRIMITIVE_TYPES = (
    (str, fields.STRING),
    (int, fields.INT),
    (bool, fields.BOOLEAN),
    (float, fields.FLOAT),
    # (bytes, "bytes"),
)

PRIMITIVE_TYPES_AND_DEFAULTS = (
    (str, "test"),
    (int, 1),
    (bool, True),
    (float, 10.4),
    # (bytes, "test".encode()),
)

PRIMITIVE_TYPES_AND_INVALID_DEFAULTS = (
    (str, 1),
    (int, "test"),
    (bool, 10),
    (float, False),
    # (bytes, "test".encode()),
)

LIST_TYPE_AND_ITEMS_TYPE = (
    (str, "string"),
    (int, "int"),
    (bool, "boolean"),
    (float, "float"),
    (bytes, "bytes"),
)

LOGICAL_TYPES = (
    (datetime.date, fields.LOGICAL_DATE, now.date()),
    (datetime.time, fields.LOGICAL_TIME, now.time()),
    (datetime.datetime, fields.LOGICAL_DATETIME, now),
    (uuid.uuid4, fields.LOGICAL_UUID, uuid.uuid4()),
)

UNION_PRIMITIVE_ELEMENTS = (
    ((str, int), (fields.STRING, fields.INT)),
    ((str, None), (fields.STRING, fields.NULL)),
    (
        (datetime.date, datetime.datetime),
        (fields.PYTHON_TYPE_TO_AVRO[datetime.date], fields.PYTHON_TYPE_TO_AVRO[datetime.datetime],),
    ),
    ((float, str, int), (fields.FLOAT, fields.STRING, fields.INT)),
    ((str, float, int, bool), (fields.STRING, fields.FLOAT, fields.INT, fields.BOOLEAN),),
)


SEQUENCE_TYPES = (typing.List, typing.Tuple, typing.Sequence, typing.MutableSequence)
MAPPING_TYPES = (typing.Dict, typing.Mapping, typing.MutableMapping)

SEQUENCES_AND_TYPES = (
    (sequence, python_type, items_type) for sequence in SEQUENCE_TYPES for python_type, items_type in PRIMITIVE_TYPES
)

SEQUENCES_LOGICAL_TYPES = (
    (sequence, python_type, items_type, value)
    for sequence in SEQUENCE_TYPES
    for python_type, items_type, value in LOGICAL_TYPES
)

MAPPING_AND_TYPES = (
    (mapping, python_type, items_type) for mapping in MAPPING_TYPES for python_type, items_type in PRIMITIVE_TYPES
)

MAPPING_LOGICAL_TYPES = (
    (mapping, python_type, items_type, value)
    for mapping in MAPPING_TYPES
    for python_type, items_type, value in LOGICAL_TYPES
)

# Represent the logical types
# (python_type, avro_internal_type, logical_type)
LOGICAL_TYPES_AND_DEFAULTS = (
    (datetime.date, fields.INT, fields.DATE),
    (datetime.time, fields.INT, fields.TIME_MILLIS),
    (datetime.datetime, fields.LONG, fields.TIMESTAMP_MILLIS),
    (uuid.uuid4, fields.STRING, fields.UUID),
)

LOGICAL_TYPES_AND_INVALID_DEFAULTS = (
    (datetime.date, 1, None),
    (datetime.time, "test", None),
    (datetime.datetime, 10, None),
    (uuid.uuid4, 10, f"Invalid default type. Default should be {str} or {uuid.UUID}"),
)


class User(AvroModel):
    "User"
    first_name: str


avro_user = {
    "name": "User",
    "type": "record",
    "doc": "User",
    "fields": [{"name": "first_name", "type": "string"}],
}

ARRAY_WITH_UNION_TYPES = (
    (typing.Union[int, str], [fields.INT, fields.STRING], [10, 20, "test"]),
    (typing.Union[int, str, User], [fields.INT, fields.STRING, avro_user], [10, 20, "test"],),
)
