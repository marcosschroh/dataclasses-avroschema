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
    (bytes, fields.BYTES),
)

PRIMITIVE_TYPES_AND_DEFAULTS = (
    (str, "test"),
    (int, 1),
    (bool, True),
    (float, 10.4),
    (bytes, b"test"),
)

PRIMITIVE_TYPES_AND_INVALID_DEFAULTS = (
    (str, 1),
    (int, "test"),
    (bool, 10),
    (float, False),
    (bytes, "test"),
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
    ((str, int), (fields.STRING, fields.INT), "test"),
    ((str, bytes), (fields.STRING, fields.BYTES), b"test"),
    ((str, None), (fields.STRING, fields.NULL), None),
    (
        (datetime.date, datetime.datetime),
        (
            fields.PYTHON_TYPE_TO_AVRO[datetime.date],
            fields.PYTHON_TYPE_TO_AVRO[datetime.datetime],
        ),
        now,
    ),
    ((float, str, int), (fields.FLOAT, fields.STRING, fields.INT), 100.0),
    ((str, float, int, bool), (fields.STRING, fields.FLOAT, fields.INT, fields.BOOLEAN), False),
)

UNION_WITH_ARRAY = (
    (
        (typing.List[int], str),
        (fields.INT, fields.STRING),
    ),
    (
        (typing.List[str], float),
        (fields.STRING, fields.FLOAT),
    ),
    (
        (typing.List[datetime.datetime], datetime.datetime),
        (fields.LOGICAL_DATETIME, fields.LOGICAL_DATETIME),
    ),
    (
        (typing.List[uuid.uuid4], bytes),
        (fields.LOGICAL_UUID, fields.BYTES),
    ),
)

UNION_WITH_MAP = (
    (
        (typing.Dict[str, int], str),
        (fields.INT, fields.STRING),
    ),
    (
        (typing.Dict[str, str], float),
        (fields.STRING, fields.FLOAT),
    ),
    (
        (typing.Dict[str, datetime.datetime], datetime.datetime),
        (fields.LOGICAL_DATETIME, fields.LOGICAL_DATETIME),
    ),
    (
        (typing.Dict[str, uuid.uuid4], bytes),
        (fields.LOGICAL_UUID, fields.BYTES),
    ),
)

OPTIONAL_UNION_COMPLEX_TYPES = (
    (typing.List[str], {"type": fields.ARRAY, "items": fields.STRING, "name": "optional_field"}),
    (
        typing.List[datetime.datetime],
        {"type": fields.ARRAY, "items": fields.LOGICAL_DATETIME, "name": "optional_field"},
    ),
    (typing.Dict[str, int], {"type": fields.MAP, "values": fields.INT, "name": "optional_field"}),
    (
        typing.Dict[str, datetime.datetime],
        {"type": fields.MAP, "values": fields.LOGICAL_DATETIME, "name": "optional_field"},
    ),
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
    (uuid.UUID, fields.STRING, fields.UUID),
)

LOGICAL_TYPES_AND_INVALID_DEFAULTS = (
    (datetime.date, 1, None),
    (datetime.time, "test", None),
    (datetime.datetime, 10, None),
    (uuid.uuid4, 10, f"Invalid default type. Default should be {str} or {uuid.UUID}"),
    (uuid.UUID, 10, f"Invalid default type. Default should be {str} or {uuid.UUID}"),
)


class User(AvroModel):
    "User"
    first_name: str


avro_user = {
    "name": "an_array_field_user_record",
    "type": "record",
    "doc": "User",
    "fields": [{"name": "first_name", "type": "string"}],
}

ARRAY_WITH_UNION_TYPES = (
    (typing.Union[int, str], [fields.INT, fields.STRING], [10, 20, "test"]),
    (
        typing.Union[int, str, User],
        [fields.INT, fields.STRING, avro_user],
        [10, 20, "test"],
    ),
)
