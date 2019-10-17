import pytest
import dataclasses
import typing
import datetime
from uuid import uuid4

from dataclasses_avroschema import fields


INMUTABLE_TYPES_AND_DEFAULTS = (
    (str, "test"),
    (int, 1),
    (bool, True),
    (float, 10.4),
    # (bytes, "test".encode()),
)

LIST_TYPE_AND_ITEMS_TYPE = (
    (str, "string"),
    (int, "int"),
    (bool, "boolean"),
    (float, "float"),
    (bytes, "bytes"),
)

now = datetime.datetime.now()

# Represent the logical types
# (python_type, avro_internal_type, logical_type)
LOGICAL_TYPES_AND_DEFAULTS = (
    (
        datetime.date,
        fields.INT,
        fields.DATE
    ),
    (
        datetime.time,
        fields.INT,
        fields.TIME_MILLIS
    ),
    (
        datetime.datetime,
        fields.LONG,
        fields.TIMESTAMP_MILLIS
    ),
    (
        uuid4,
        fields.STRING,
        fields.UUID
    )
)


def test_invalid_type_field():
    python_type = typing.Set
    name = "test_field"
    msg = f"Invalid Type for field {name}. Accepted types are list, tuple, dict or typing.Union"

    with pytest.raises(ValueError, match=msg):
        fields.Field(name, python_type, dataclasses.MISSING)


@pytest.mark.parametrize("inmutable_type", fields.PYTHON_INMUTABLE_TYPES)
def test_inmutable_types(inmutable_type):
    name = "a_field"
    field = fields.Field(name, inmutable_type, dataclasses.MISSING)
    avro_type = fields.PYTHON_TYPE_TO_AVRO[inmutable_type]

    assert {"name": name, "type": avro_type} == field.to_dict()


@pytest.mark.parametrize("inmutable_type", fields.PYTHON_INMUTABLE_TYPES)
def test_inmutable_types_with_default_value_none(inmutable_type):
    name = "a_field"
    field = fields.Field(name, inmutable_type, None)
    avro_type = [fields.NULL, fields.PYTHON_TYPE_TO_AVRO[inmutable_type]]

    assert {"name": name, "type": avro_type, "default": fields.NULL} == field.to_dict()


@pytest.mark.parametrize("inmutable_type,default", INMUTABLE_TYPES_AND_DEFAULTS)
def test_inmutable_types_with_default_value(inmutable_type, default):
    name = "a_field"
    field = fields.Field(name, inmutable_type, default)
    avro_type = [fields.PYTHON_TYPE_TO_AVRO[inmutable_type], fields.NULL]

    assert {"name": name, "type": avro_type, "default": default} == field.to_dict()


def test_tuple_type():
    """
    When the type is Tuple, the Avro field type should be enum
    with the symbols attribute present.
    """
    name = "an_enum_field"
    default = ("BLUE", "YELOW", "RED",)
    python_type = typing.Tuple
    field = fields.Field(name, python_type, default)

    expected = {
        "name": name,
        "type": {
            "type": "enum",
            "name": name,
            "symbols": list(default)
        }
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_primitive_type,python_type_str", LIST_TYPE_AND_ITEMS_TYPE)
def test_list_type(python_primitive_type, python_type_str):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = typing.List[python_primitive_type]
    field = fields.Field(name, python_type, dataclasses.MISSING)

    expected = {
        "name": name,
        "type": {
            "type": "array",
            "name": name,
            "items": python_type_str
        }
    }

    assert expected == field.to_dict()


def test_list_type_default_value():
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = typing.List[int]

    field = fields.Field(name, python_type, None)
    expected = {
        "name": name,
        "type": {
            "type": "array",
            "name": name,
            "items": "int"
        },
        "default": []
    }

    assert expected == field.to_dict()

    field = fields.Field(name, python_type, default=dataclasses.MISSING, default_factory=lambda: [1, 2])

    expected = {
        "name": name,
        "type": {
            "type": "array",
            "name": name,
            "items": "int"
        },
        "default": [1, 2]
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_primitive_type,python_type_str", LIST_TYPE_AND_ITEMS_TYPE)
def test_dict_type(python_primitive_type, python_type_str):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = typing.Dict[str, python_primitive_type]
    field = fields.Field(name, python_type, dataclasses.MISSING)

    expected = {
        "name": name,
        "type": {
            "type": "map",
            "name": name,
            "values": python_type_str
        }
    }

    assert expected == field.to_dict()


def test_dict_type_default_value():
    """
    When the type is Dict, the Avro field type should be a map
    with the values attribute present.
    """

    name = "a_map_field"
    python_type = typing.Dict[str, int]

    field = fields.Field(name, python_type, None)

    expected = {
        "name": name,
        "type": {
            "type": "map",
            "name": name,
            "values": "int"
        },
        "default": {}
    }
    assert expected == field.to_dict()

    field = fields.Field(name, python_type, default=dataclasses.MISSING, default_factory=lambda: {"key": 1})

    expected = {
        "name": name,
        "type": {
            "type": "map",
            "name": name,
            "values": "int"
        },
        "default": {"key": 1}
    }

    assert expected == field.to_dict()


def test_union_type():
    class User:
        "User"
        first_name: str

    class Car:
        "Car"
        engine_name: str

    name = "an_union_field"
    python_type = typing.Union[User, Car]

    field = fields.Field(name, python_type)

    expected = {
        "name": name,
        "type": [
            {
                "name": "User",
                "type": "record",
                "doc": "User",
                "fields": [
                    {"name": "first_name", "type": "string"}
                ]
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [
                    {"name": "engine_name", "type": "string"}
                ]
            }
        ]
    }

    assert expected == field.to_dict()


def test_union_type_default_value():
    class User:
        "User"
        first_name: str

    class Car:
        "Car"
        engine_name: str

    name = "an_union_field"
    python_type = typing.Union[User, Car]
    field = fields.Field(name, python_type, None)

    expected = {
        "name": name,
        "type": [
            fields.NULL,
            {
                "name": "User",
                "type": "record",
                "doc": "User",
                "fields": [
                    {"name": "first_name", "type": "string"}
                ]
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [
                    {"name": "engine_name", "type": "string"}
                ]
            }
        ],
        "default": fields.NULL
    }

    assert expected == field.to_dict()

    field = fields.Field(
        name, python_type,
        default=dataclasses.MISSING,
        default_factory=lambda: {"first_name": "a name"}
    )

    expected = {
        "name": name,
        "type": [
            {
                "name": "User",
                "type": "record",
                "doc": "User",
                "fields": [
                    {"name": "first_name", "type": "string"}
                ]
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [
                    {"name": "engine_name", "type": "string"}
                ]
            }
        ],
        "default": {"first_name": "a name"}
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_type,avro_type,logical_type", LOGICAL_TYPES_AND_DEFAULTS)
def test_logical_types(python_type, avro_type, logical_type):
    name = "a logical type"
    python_type = python_type
    field = fields.Field(name, python_type)

    expected = {
        "name": name,
        "type":  {
            "type": avro_type,
            "logicalType": logical_type
        }
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_type,avro_type,logical_type", LOGICAL_TYPES_AND_DEFAULTS)
def test_logical_types_with_null_as_default(python_type, avro_type, logical_type):
    name = "a logical type"
    python_type = python_type
    field = fields.Field(name, python_type, None)

    expected = {
        "name": name,
        "type":  {
            "type": avro_type,
            "logicalType": logical_type
        },
        "default": fields.NULL
    }

    assert expected == field.to_dict()


def test_logical_type_date_with_default():
    name = "a date"
    python_type = datetime.date
    field = fields.Field(name, python_type, now)

    date_time = datetime.datetime.combine(now, datetime.datetime.min.time())
    ts = (date_time - datetime.datetime(1970, 1, 1)).total_seconds()

    expected = {
        "name": name,
        "type":  {
            "type": fields.INT,
            "logicalType": fields.DATE
        },
        "default": ts / (3600 * 24)
    }

    assert expected == field.to_dict()


def test_logical_type_time_with_default():
    name = "a time"
    python_type = datetime.time
    time = now.time()
    field = fields.Field(name, python_type, time)

    hour, minutes, seconds, microseconds = time.hour, time.minute, time.second, time.microsecond
    miliseconds = int((((hour * 60 + minutes) * 60 + seconds) * 1000) + (microseconds / 1000))

    expected = {
        "name": name,
        "type":  {
            "type": fields.INT,
            "logicalType": fields.TIME_MILLIS
        },
        "default": miliseconds
    }

    assert expected == field.to_dict()


def test_logical_type_datetime_with_default():
    name = "a datetime"
    python_type = datetime.datetime
    field = fields.Field(name, python_type, now)

    ts = (now - datetime.datetime(1970, 1, 1)).total_seconds()

    expected = {
        "name": name,
        "type":  {
            "type": fields.LONG,
            "logicalType": fields.TIMESTAMP_MILLIS
        },
        "default": ts * 1000
    }

    assert expected == field.to_dict()


def test_logical_type_uuid_with_default():
    name = "a uuid"
    python_type = uuid4
    default = uuid4()
    field = fields.Field(name, python_type, default)

    expected = {
        "name": name,
        "type":  {
            "type": fields.STRING,
            "logicalType": fields.UUID
        },
        "default": str(default)
    }

    assert expected == field.to_dict()
