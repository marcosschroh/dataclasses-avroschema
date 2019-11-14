import pytest
import dataclasses
import typing
import datetime
import uuid

from faker import Faker

from dataclasses_avroschema import fields

faker = Faker()


PRIMITIVE_TYPES_AND_LOGICAL = (
    (str, fields.STRING),
    (int, fields.INT),
    (bool, fields.BOOLEAN),
    (float, fields.FLOAT),
    # (bytes, "bytes"),
    # (datetime.date, fields.LOGICAL_DATE),
    # (datetime.time, fields.LOGICAL_TIME),
    # (datetime.datetime, fields.LOGICAL_DATETIME),
    (uuid.uuid4, fields.LOGICAL_UUID),
)

UNION_PRIMITIVE_ELEMENTS = (
    ((str, int), (fields.STRING, fields.INT)),
    (
        (datetime.date, datetime.datetime),
        (
            fields.PYTHON_TYPE_TO_AVRO[datetime.date],
            fields.PYTHON_TYPE_TO_AVRO[datetime.datetime],
        ),
    ),
    ((float, str, int), (fields.FLOAT, fields.STRING, fields.INT)),
    (
        (str, float, int, bool),
        (fields.STRING, fields.FLOAT, fields.INT, fields.BOOLEAN),
    ),
)


SEQUENCE_TYPES = (typing.List, typing.Sequence, typing.MutableSequence)
MAPPING_TYPES = (typing.Dict, typing.Mapping, typing.MutableMapping)

SEQUENCES_AND_TYPES = (
    (sequence, python_type, items_type)
    for sequence in SEQUENCE_TYPES
    for python_type, items_type in PRIMITIVE_TYPES_AND_LOGICAL
)

MAPPING_AND_TYPES = (
    (sequence, python_type, items_type)
    for sequence in MAPPING_TYPES
    for python_type, items_type in PRIMITIVE_TYPES_AND_LOGICAL
)


def test_invalid_type_container_field():
    python_type = typing.Set
    name = "test_field"
    msg = f"Invalid Type for field {name}. Accepted types are list, tuple, dict or typing.Union"

    with pytest.raises(ValueError, match=msg):
        fields.Field(name, python_type, dataclasses.MISSING)


def test_tuple_type():
    """
    When the type is Tuple, the Avro field type should be enum
    with the symbols attribute present.
    """
    name = "an_enum_field"
    default = ("BLUE", "YELOW", "RED")
    python_type = typing.Tuple
    field = fields.Field(name, python_type, default)

    expected = {
        "name": name,
        "type": {"type": "enum", "name": name, "symbols": list(default)},
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize(
    "sequence, python_primitive_type,python_type_str", SEQUENCES_AND_TYPES
)
def test_sequence_type(sequence, python_primitive_type, python_type_str):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[python_primitive_type]
    field = fields.Field(name, python_type, dataclasses.MISSING)

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
    }

    assert expected == field.to_dict()

    python_type = sequence[python_primitive_type]
    field = fields.Field(name, python_type, None)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [],
    }

    assert expected == field.to_dict()

    if python_primitive_type is datetime.datetime:
        python_primitive_type = "date_time"

    values = faker.pylist(2, True, python_primitive_type)
    field = fields.Field(
        name, python_type, default=dataclasses.MISSING, default_factory=lambda: values
    )

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": values,
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize(
    "mapping,python_primitive_type,python_type_str", MAPPING_AND_TYPES
)
def test_mapping_type(mapping, python_primitive_type, python_type_str):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = mapping[str, python_primitive_type]
    field = fields.Field(name, python_type, dataclasses.MISSING)

    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.Field(name, python_type, None)

    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": {},
    }
    assert expected == field.to_dict()

    if python_primitive_type is datetime.datetime:
        python_primitive_type = "date_time"

    value = faker.pydict(2, True, python_primitive_type)
    field = fields.Field(
        name, python_type, default=dataclasses.MISSING, default_factory=lambda: value
    )

    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": value,
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("args", UNION_PRIMITIVE_ELEMENTS)
def test_union_type(args):
    primitive_types, avro_types = args[0], args[1]

    name = "an_union_field"
    python_type = typing.Union[primitive_types]
    field = fields.Field(name, python_type)

    expected = {"name": name, "type": [*avro_types]}

    assert expected == field.to_dict()


def test_union_type_with_records():
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
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
    }

    assert expected == field.to_dict()


def test_union_type_with_record_default():
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
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
        "default": fields.NULL,
    }

    assert expected == field.to_dict()

    field = fields.Field(
        name,
        python_type,
        default=dataclasses.MISSING,
        default_factory=lambda: {"first_name": "a name"},
    )

    expected = {
        "name": name,
        "type": [
            {
                "name": "User",
                "type": "record",
                "doc": "User",
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
        "default": {"first_name": "a name"},
    }

    assert expected == field.to_dict()
