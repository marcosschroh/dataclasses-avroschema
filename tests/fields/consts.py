import datetime
import sys
import typing
import uuid

import pytest

from dataclasses_avroschema import field_utils, fields

PY_VER = sys.version_info

now = datetime.datetime.now()

PRIMITIVE_TYPES = (
    (str, fields.STRING),
    (int, fields.LONG),
    (bool, fields.BOOLEAN),
    (float, fields.DOUBLE),
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
    (int, "long"),
    (bool, "boolean"),
    (float, "double"),
    (bytes, "bytes"),
)

LOGICAL_TYPES = (
    (datetime.date, fields.LOGICAL_DATE, now.date()),
    (datetime.time, fields.LOGICAL_TIME_MILIS, now.time()),
    (datetime.datetime, fields.LOGICAL_DATETIME_MILIS, now),
    (uuid.uuid4, fields.LOGICAL_UUID, uuid.uuid4()),
)

UNION_PRIMITIVE_ELEMENTS = (
    ((str, int), (fields.STRING, fields.LONG), "test"),
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
    ((float, str, int), (fields.DOUBLE, fields.STRING, fields.LONG), 100.0),
    ((str, float, int, bool), (fields.STRING, fields.DOUBLE, fields.LONG, fields.BOOLEAN), False),
)

UNION_PRIMITIVE_ELEMENTS_DEFAULTS = (
    ((str, int), (fields.STRING, fields.LONG), "test"),
    ((str, bytes), (fields.BYTES, fields.STRING), b"test"),
    ((str, None), (fields.NULL, fields.STRING), None),
    (
        (datetime.date, datetime.datetime),
        (
            fields.PYTHON_TYPE_TO_AVRO[datetime.datetime],
            fields.PYTHON_TYPE_TO_AVRO[datetime.date],
        ),
        now,
    ),
    ((float, str, int), (fields.DOUBLE, fields.STRING, fields.LONG), 100.0),
    ((str, float, int, bool), (fields.BOOLEAN, fields.STRING, fields.DOUBLE, fields.LONG), False),
)

UNION_WITH_ARRAY = (
    (
        (typing.List[int], str),
        (fields.LONG, fields.STRING),
    ),
    (
        (typing.List[str], float),
        (fields.STRING, fields.DOUBLE),
    ),
    (
        (typing.List[datetime.datetime], datetime.datetime),
        (fields.LOGICAL_DATETIME_MILIS, fields.LOGICAL_DATETIME_MILIS),
    ),
    (
        (typing.List[uuid.uuid4], bytes),
        (fields.LOGICAL_UUID, fields.BYTES),
    ),
)

UNION_WITH_MAP = (
    (
        (typing.Dict[str, int], str),
        (fields.LONG, fields.STRING),
    ),
    (
        (typing.Dict[str, str], float),
        (fields.STRING, fields.DOUBLE),
    ),
    (
        (typing.Dict[str, datetime.datetime], datetime.datetime),
        (fields.LOGICAL_DATETIME_MILIS, fields.LOGICAL_DATETIME_MILIS),
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
        {"type": fields.ARRAY, "items": fields.LOGICAL_DATETIME_MILIS, "name": "optional_field"},
    ),
    (typing.Dict[str, int], {"type": fields.MAP, "values": fields.LONG, "name": "optional_field"}),
    (
        typing.Dict[str, datetime.datetime],
        {"type": fields.MAP, "values": fields.LOGICAL_DATETIME_MILIS, "name": "optional_field"},
    ),
)


def xfail_annotation(typ):
    return pytest.mark.xfail(
        (typ in (list, tuple, dict) and PY_VER < (3, 9)),
        reason="Standard collection annotations not supported - see PEP585.",
    )


SEQUENCE_TYPES = (typing.List, typing.Tuple, typing.Sequence, typing.MutableSequence, list, tuple)
MAPPING_TYPES = (typing.Dict, typing.Mapping, typing.MutableMapping, dict)

SEQUENCES_AND_TYPES = [
    pytest.param(sequence, python_type, items_type, marks=xfail_annotation(sequence))
    for sequence in SEQUENCE_TYPES
    for python_type, items_type in PRIMITIVE_TYPES
]

SEQUENCES_LOGICAL_TYPES = [
    pytest.param(sequence, python_type, items_type, value, marks=xfail_annotation(sequence))
    for sequence in SEQUENCE_TYPES
    for python_type, items_type, value in LOGICAL_TYPES
]

MAPPING_AND_TYPES = [
    pytest.param(mapping, python_type, items_type, marks=xfail_annotation(mapping))
    for mapping in MAPPING_TYPES
    for python_type, items_type in PRIMITIVE_TYPES
]

MAPPING_LOGICAL_TYPES = [
    pytest.param(mapping, python_type, items_type, value, marks=xfail_annotation(mapping))
    for mapping in MAPPING_TYPES
    for python_type, items_type, value in LOGICAL_TYPES
]

# Represent the logical types
# (python_type, avro_internal_type, logical_type)
LOGICAL_TYPES_AND_DEFAULTS = (
    (datetime.date, fields.INT, fields.DATE),
    (datetime.time, fields.INT, field_utils.TIME_MILLIS),
    (datetime.datetime, fields.LONG, field_utils.TIMESTAMP_MILLIS),
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


ARRAY_WITH_UNION_TYPES = (
    (typing.Union[int, str], [fields.LONG, fields.STRING], [10, 20, "test"]),
    (
        typing.Union[int, str, float],
        [fields.LONG, fields.STRING, fields.DOUBLE],
        [10, 20, 100.9],
    ),
)
