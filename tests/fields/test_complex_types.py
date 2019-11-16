import pytest
import dataclasses
import typing

from faker import Faker

from dataclasses_avroschema import fields

from . import consts

faker = Faker()


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
    "sequence, python_primitive_type,python_type_str", consts.SEQUENCES_AND_TYPES
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

    field = fields.Field(name, python_type, None)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [],
    }

    assert expected == field.to_dict()

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
    "sequence,python_primitive_type,python_type_str,value",
    consts.SEQUENCES_LOGICAL_TYPES,
)
def test_sequence_with_logical_type(
    sequence, python_primitive_type, python_type_str, value
):
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

    field = fields.Field(name, python_type, None)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [],
    }

    assert expected == field.to_dict()

    values = [value]

    field = fields.Field(
        name, python_type, default=dataclasses.MISSING, default_factory=lambda: values
    )

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [
            fields.LOGICAL_TYPES_FIELDS_CLASSES[python_primitive_type].to_logical_type(
                value
            )
            for value in values
        ],
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize(
    "mapping,python_primitive_type,python_type_str", consts.MAPPING_AND_TYPES
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


@pytest.mark.parametrize(
    "mapping,python_primitive_type,python_type_str,value", consts.MAPPING_LOGICAL_TYPES
)
def test_mapping_logical_type(mapping, python_primitive_type, python_type_str, value):
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

    values = {"key": value}
    field = fields.Field(
        name, python_type, default=dataclasses.MISSING, default_factory=lambda: values
    )

    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": {
            key: fields.LOGICAL_TYPES_FIELDS_CLASSES[
                python_primitive_type
            ].to_logical_type(value)
            for key, value in values.items()
        },
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("args", consts.UNION_PRIMITIVE_ELEMENTS)
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
