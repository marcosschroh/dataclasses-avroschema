import datetime
import sys
import typing
import uuid

import pydantic
import pytest
from typing_extensions import Annotated

from dataclasses_avroschema.fields import field_utils

PY_VER = sys.version_info

now = datetime.datetime.now(tz=datetime.timezone.utc)

PRIMITIVE_TYPES = (
    (str, field_utils.STRING),
    (int, field_utils.LONG),
    (bool, field_utils.BOOLEAN),
    (float, field_utils.DOUBLE),
    (bytes, field_utils.BYTES),
    (None, field_utils.NULL),
    (type(None), field_utils.NULL),
    (Annotated[str, "string"], field_utils.STRING),
    (Annotated[int, "integer"], field_utils.LONG),
    (Annotated[bool, "boolean"], field_utils.BOOLEAN),
    (Annotated[float, "float"], field_utils.DOUBLE),
    (Annotated[bytes, "bytes"], field_utils.BYTES),
    # pydantic fields
    (pydantic.FilePath, {"type": field_utils.STRING, "pydantic-class": "FilePath"}),
    (pydantic.DirectoryPath, {"type": field_utils.STRING, "pydantic-class": "DirectoryPath"}),
    (pydantic.EmailStr, {"type": field_utils.STRING, "pydantic-class": "EmailStr"}),
    (pydantic.NameEmail, {"type": field_utils.STRING, "pydantic-class": "NameEmail"}),
    (pydantic.AnyUrl, {"type": field_utils.STRING, "pydantic-class": "AnyUrl"}),
    (pydantic.AnyHttpUrl, {"type": field_utils.STRING, "pydantic-class": "AnyHttpUrl"}),
    (pydantic.HttpUrl, {"type": field_utils.STRING, "pydantic-class": "HttpUrl"}),
    (pydantic.FileUrl, {"type": field_utils.STRING, "pydantic-class": "FileUrl"}),
    (pydantic.PostgresDsn, {"type": field_utils.STRING, "pydantic-class": "PostgresDsn"}),
    (pydantic.CockroachDsn, {"type": field_utils.STRING, "pydantic-class": "CockroachDsn"}),
    (pydantic.AmqpDsn, {"type": field_utils.STRING, "pydantic-class": "AmqpDsn"}),
    (pydantic.RedisDsn, {"type": field_utils.STRING, "pydantic-class": "RedisDsn"}),
    (pydantic.MongoDsn, {"type": field_utils.STRING, "pydantic-class": "MongoDsn"}),
    (pydantic.KafkaDsn, {"type": field_utils.STRING, "pydantic-class": "KafkaDsn"}),
    (pydantic.SecretStr, {"type": field_utils.STRING, "pydantic-class": "SecretStr"}),
    (pydantic.IPvAnyAddress, {"type": field_utils.STRING, "pydantic-class": "IPvAnyAddress"}),
    (pydantic.IPvAnyInterface, {"type": field_utils.STRING, "pydantic-class": "IPvAnyInterface"}),
    (pydantic.IPvAnyNetwork, {"type": field_utils.STRING, "pydantic-class": "IPvAnyNetwork"}),
    (pydantic.NegativeFloat, {"type": field_utils.DOUBLE, "pydantic-class": "NegativeFloat"}),
    (pydantic.PositiveFloat, {"type": field_utils.DOUBLE, "pydantic-class": "PositiveFloat"}),
    (pydantic.NegativeInt, {"type": field_utils.LONG, "pydantic-class": "NegativeInt"}),
    (pydantic.PositiveInt, {"type": field_utils.LONG, "pydantic-class": "PositiveInt"}),
)

PRIMITIVE_TYPES_AND_DEFAULTS = (
    (str, "test"),
    (int, 1),
    (bool, True),
    (float, 10.4),
    (bytes, b"test"),
    (None, None),
    (type(None), None),
    (Annotated[str, "string"], "test"),
    (Annotated[int, "int"], 1),
    (Annotated[bool, "boolean"], True),
    (Annotated[float, "float"], 10.4),
    (Annotated[bytes, "bytes"], b"test"),
    # test the subclasses types are also allowed
    (float, 10),
)

PRIMITIVE_TYPES_AND_INVALID_DEFAULTS = (
    (str, 1),
    (int, "test"),
    (bool, 10),
    (float, "test"),
    (bytes, "test"),
    (None, 1),
    (type(None), "test"),
)

LOGICAL_TYPES = (
    (datetime.date, field_utils.LOGICAL_DATE, now.date()),
    (datetime.time, field_utils.LOGICAL_TIME_MILIS, now.time()),
    (datetime.datetime, field_utils.LOGICAL_DATETIME_MILIS, now),
    (uuid.UUID, field_utils.LOGICAL_UUID, uuid.uuid4()),
    (Annotated[datetime.date, "date"], field_utils.LOGICAL_DATE, now.date()),
    (Annotated[datetime.time, "time"], field_utils.LOGICAL_TIME_MILIS, now.time()),
    (Annotated[datetime.datetime, "datetime"], field_utils.LOGICAL_DATETIME_MILIS, now),
    (Annotated[uuid.UUID, "uuid"], field_utils.LOGICAL_UUID, uuid.uuid4()),
)

UNION_PRIMITIVE_ELEMENTS = (
    (
        typing.Union[str, int],
        (field_utils.STRING, field_utils.LONG),
    ),
    (
        typing.Union[str, bytes],
        (field_utils.STRING, field_utils.BYTES),
    ),
    (
        typing.Union[str, None],
        (field_utils.STRING, field_utils.NULL),
    ),
    (
        typing.Union[datetime.date, datetime.datetime],
        (
            field_utils.PYTHON_TYPE_TO_AVRO[datetime.date],
            field_utils.PYTHON_TYPE_TO_AVRO[datetime.datetime],
        ),
    ),
    (typing.Union[float, str, int], (field_utils.DOUBLE, field_utils.STRING, field_utils.LONG)),
    (
        typing.Union[str, float, int, bool],
        (field_utils.STRING, field_utils.DOUBLE, field_utils.LONG, field_utils.BOOLEAN),
    ),
    (
        typing.Union[Annotated[str, "string"], int],
        (field_utils.STRING, field_utils.LONG),
    ),
)

UNION_PRIMITIVE_ELEMENTS_DEFAULTS = (
    (typing.Union[str, int], (field_utils.STRING, field_utils.LONG), "test"),
    (typing.Union[bytes, str], (field_utils.BYTES, field_utils.STRING), b"test"),
    (typing.Union[str, None], (field_utils.NULL, field_utils.STRING), None),
    (
        typing.Union[datetime.date, datetime.datetime],
        (
            field_utils.PYTHON_TYPE_TO_AVRO[datetime.datetime],
            field_utils.PYTHON_TYPE_TO_AVRO[datetime.date],
        ),
        now,
    ),
    (typing.Union[float, str, int], (field_utils.DOUBLE, field_utils.STRING, field_utils.LONG), 100.0),
    (
        typing.Union[bool, str, float, int],
        (field_utils.BOOLEAN, field_utils.STRING, field_utils.DOUBLE, field_utils.LONG),
        False,
    ),
    (typing.Union[Annotated[str, "string"], int], (field_utils.STRING, field_utils.LONG), "test"),
)

UNION_WITH_ARRAY = (
    (
        typing.Union[typing.List[int], str],
        (field_utils.LONG, field_utils.STRING),
    ),
    (
        typing.Union[typing.List[str], float],
        (field_utils.STRING, field_utils.DOUBLE),
    ),
    (
        typing.Union[typing.List[datetime.datetime], datetime.datetime],
        (field_utils.LOGICAL_DATETIME_MILIS, field_utils.LOGICAL_DATETIME_MILIS),
    ),
    (
        typing.Union[typing.List[uuid.UUID], bytes],
        (field_utils.LOGICAL_UUID, field_utils.BYTES),
    ),
    (
        typing.Union[typing.List[Annotated[int, "integer"]], str],
        (field_utils.LONG, field_utils.STRING),
    ),
)

UNION_WITH_MAP = (
    (
        typing.Union[typing.Dict[str, int], str],
        (field_utils.LONG, field_utils.STRING),
    ),
    (
        typing.Union[typing.Dict[str, str], float],
        (field_utils.STRING, field_utils.DOUBLE),
    ),
    (
        typing.Union[typing.Dict[str, datetime.datetime], datetime.datetime],
        (field_utils.LOGICAL_DATETIME_MILIS, field_utils.LOGICAL_DATETIME_MILIS),
    ),
    (
        typing.Union[typing.Dict[str, uuid.UUID], bytes],
        (field_utils.LOGICAL_UUID, field_utils.BYTES),
    ),
    (
        typing.Union[typing.Dict[str, Annotated[int, "integer"]], str],
        (field_utils.LONG, field_utils.STRING),
    ),
)

OPTIONAL_UNION_COMPLEX_TYPES = (
    (typing.List[str], {"type": field_utils.ARRAY, "items": field_utils.STRING, "name": "optional_field"}),
    (
        typing.List[datetime.datetime],
        {"type": field_utils.ARRAY, "items": field_utils.LOGICAL_DATETIME_MILIS, "name": "optional_field"},
    ),
    (typing.Dict[str, int], {"type": field_utils.MAP, "values": field_utils.LONG, "name": "optional_field"}),
    (
        typing.Dict[str, datetime.datetime],
        {"type": field_utils.MAP, "values": field_utils.LOGICAL_DATETIME_MILIS, "name": "optional_field"},
    ),
)

# Add the new syntax | for unions
if PY_VER >= (3, 10):
    UNION_PRIMITIVE_ELEMENTS += (  # type: ignore
        (
            str | int,
            (field_utils.STRING, field_utils.LONG),
        ),
        (
            str | bytes,
            (field_utils.STRING, field_utils.BYTES),
        ),
        (
            str | None,
            (field_utils.STRING, field_utils.NULL),
        ),
        (
            datetime.date | datetime.datetime,
            (
                field_utils.PYTHON_TYPE_TO_AVRO[datetime.date],
                field_utils.PYTHON_TYPE_TO_AVRO[datetime.datetime],
            ),
        ),
        (float | str | int, (field_utils.DOUBLE, field_utils.STRING, field_utils.LONG)),
        (
            typing.Union[str, float, int, bool],
            (field_utils.STRING, field_utils.DOUBLE, field_utils.LONG, field_utils.BOOLEAN),
        ),
    )

    UNION_PRIMITIVE_ELEMENTS_DEFAULTS += (  # type: ignore
        (str | int, (field_utils.STRING, field_utils.LONG), "test"),
        (str | bytes, (field_utils.BYTES, field_utils.STRING), b"test"),
        (str | None, (field_utils.NULL, field_utils.STRING), None),
        (
            datetime.date | datetime.datetime,
            (
                field_utils.PYTHON_TYPE_TO_AVRO[datetime.datetime],
                field_utils.PYTHON_TYPE_TO_AVRO[datetime.date],
            ),
            now,
        ),
        (float | str | int, (field_utils.DOUBLE, field_utils.STRING, field_utils.LONG), 100.0),
        (
            str | float | int | bool,
            (field_utils.BOOLEAN, field_utils.STRING, field_utils.DOUBLE, field_utils.LONG),
            False,
        ),
    )

    UNION_WITH_ARRAY += (  # type: ignore
        (
            typing.List[int] | str,  # in python is translated to typing.Union[typing.List[int], str]
            (field_utils.LONG, field_utils.STRING),
        ),
        (
            typing.List[str] | float,
            (field_utils.STRING, field_utils.DOUBLE),
        ),
        (
            typing.List[datetime.datetime] | datetime.datetime,
            (field_utils.LOGICAL_DATETIME_MILIS, field_utils.LOGICAL_DATETIME_MILIS),
        ),
        (
            typing.List[uuid.UUID] | bytes,
            (field_utils.LOGICAL_UUID, field_utils.BYTES),
        ),
    )

    UNION_WITH_MAP += (  # type: ignore
        (
            typing.Dict[str, int] | str,  # in python is translated to typing.Union[typing.Dict[str, int], str]
            (field_utils.LONG, field_utils.STRING),
        ),
        (
            typing.Dict[str, str] | float,
            (field_utils.STRING, field_utils.DOUBLE),
        ),
        (
            typing.Dict[str, datetime.datetime] | datetime.datetime,
            (field_utils.LOGICAL_DATETIME_MILIS, field_utils.LOGICAL_DATETIME_MILIS),
        ),
        (
            typing.Dict[str, uuid.UUID] | bytes,
            (field_utils.LOGICAL_UUID, field_utils.BYTES),
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
# (python_type, avro_type)
LOGICAL_TYPES_AND_DEFAULTS = (
    (datetime.date, {"type": field_utils.INT, "logicalType": field_utils.DATE}),
    (datetime.time, {"type": field_utils.INT, "logicalType": field_utils.TIME_MILLIS}),
    (datetime.datetime, {"type": field_utils.LONG, "logicalType": field_utils.TIMESTAMP_MILLIS}),
    (uuid.uuid4, {"type": field_utils.STRING, "logicalType": field_utils.UUID}),
    (uuid.UUID, {"type": field_utils.STRING, "logicalType": field_utils.UUID}),
)

LOGICAL_TYPES_AND_INVALID_DEFAULTS = (
    (datetime.date, 1, None),
    (datetime.time, "test", None),
    (datetime.datetime, 10, None),
    (uuid.uuid4, 10, f"Invalid default type. Default should be {str} or {uuid.UUID}"),
    (uuid.UUID, 10, f"Invalid default type. Default should be {str} or {uuid.UUID}"),
)


ARRAY_WITH_UNION_TYPES = (
    (typing.Union[int, str], [field_utils.LONG, field_utils.STRING], [10, 20, "test"]),
    (
        typing.Union[int, str, float],
        [field_utils.LONG, field_utils.STRING, field_utils.DOUBLE],
        [10, 20, 100.9],
    ),
)
