import pytest
import dataclasses
import typing

from dataclasses_avroschema import fields

LIST_TYPE_AND_ITEMS_TYPE = (
    (str, "string"),
    (int, "int"),
    (bool, "boolean"),
    (float, "float"),
    (bytes, "bytes"),
)


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
