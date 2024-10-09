import json
import math
from typing import Any, Optional

import pytest
from pydantic import (
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    ValidationError,
    conint,
    field_serializer,
)
from pydantic_core import core_schema

from dataclasses_avroschema import AVRO, AVRO_JSON, types
from dataclasses_avroschema.pydantic import AvroBaseModel


class CustomClass:
    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        def validate(value):
            if isinstance(value, CustomClass):
                return value
            elif not isinstance(value, str):
                raise ValueError(f"Value must be a string or CustomClass - not {type(value)}")

            return cls(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(CustomClass),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: instance.x),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CustomClass):
            return NotImplemented

        return self.value == other.value

    def __str__(self) -> str:
        return f"{self.value}"


class Parent(AvroBaseModel):
    model_config = ConfigDict(json_encoders={CustomClass: str}, arbitrary_types_allowed=True)
    custom_class: CustomClass

    @field_serializer("custom_class")
    def serialize_custom_class(self, custom_class: CustomClass, _info):
        return str(custom_class)


parent_under_test = Parent(custom_class=CustomClass("custom class value"))
parent_avro_binary = b"$custom class value"
parent_avro_json = b'{"custom_class": "custom class value"}'


def test_int_constrained_type_serialize():
    class ConstrainedType(AvroBaseModel):
        value: conint(gt=0)

    c = ConstrainedType(value=1)
    serialized = c.serialize(serialization_type="avro-json")
    assert serialized == b'{"value": 1}'


def test_int_constrained_type_deserialize():
    class ConstrainedType(AvroBaseModel):
        value: conint(gt=0)

    c = ConstrainedType(value=1)
    deserialized = ConstrainedType.deserialize(b'{"value": 1}', serialization_type="avro-json")
    assert deserialized == c


def test_int_constrained_type_deserialize_invalid():
    class ConstrainedType(AvroBaseModel):
        value: int = Field(gt=0)

    with pytest.raises(ValidationError):
        ConstrainedType.deserialize(b'{"value": 0}', serialization_type="avro-json")


@pytest.mark.parametrize(
    "serialization_type, expected_result",
    [(AVRO, parent_avro_binary), (AVRO_JSON, parent_avro_json)],
)
def test_custom_class_type_serialize(serialization_type: str, expected_result: bytes):
    serialized = parent_under_test.serialize(serialization_type)
    assert serialized == expected_result


@pytest.mark.parametrize(
    "serialization_type, data",
    [(AVRO, parent_avro_binary), (AVRO_JSON, parent_avro_json)],
)
def test_custom_class_type_deserialize(serialization_type: str, data: bytes):
    deserialized = Parent.deserialize(data, serialization_type)
    assert deserialized == parent_under_test


def test_custom_class_deserialize_invalid():
    with pytest.raises(ValidationError):
        Parent.deserialize(b'{"custom_class": 1}', serialization_type="avro-json")


def test_primitive_types_with_defaults():
    class User(AvroBaseModel):
        name: str = "marcos"
        age: int = 20
        has_pets: bool = False
        money: float = 100.0
        encoded: bytes = b"hola"
        height: types.Int32 = 184

    data = {
        "name": "marcos",
        "age": 20,
        "has_pets": False,
        "money": 100.0,
        "encoded": b"hola",
        "height": 184,
    }
    data_json = {
        "name": "marcos",
        "age": 20,
        "has_pets": False,
        "money": 100.0,
        "encoded": "hola",
        "height": 184,
    }

    user = User()
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data_json)

    # check that works with schema evolution
    user = User(name="Juan", age=30)
    avro_json = user.serialize(serialization_type="avro-json")

    data = {
        "name": "Juan",
        "age": 30,
        "has_pets": False,
        "money": 100.0,
        "encoded": b"hola",
        "height": 184,
    }
    data_json = {
        "name": "Juan",
        "age": 30,
        "has_pets": False,
        "money": 100.0,
        "encoded": "hola",
        "height": 184,
    }

    # assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    # assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user
    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data_json)


def test_exclude_default_from_schema():
    class User(AvroBaseModel):
        name: str = Field(default="marcos", metadata={"exclude_default": True})
        age: int = Field(default=20, metadata={"exclude_default": True})

    assert User.avro_schema_to_python() == {
        "type": "record",
        "name": "User",
        "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}],
    }

    user = User()
    data = {"name": "marcos", "age": 20}
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data)


def test_primitive_types_with_nulls():
    class User(AvroBaseModel):
        name: Optional[str] = None
        age: Optional[int] = 20
        has_pets: Optional[bool] = False
        money: Optional[float] = None
        encoded: Optional[bytes] = None
        height: Optional[types.Int32] = None

    data = {
        "name": None,
        "age": 20,
        "has_pets": False,
        "money": 100.0,
        "encoded": b"hola",
        "height": 184,
    }
    data_json = {
        "name": None,
        "age": 20,
        "has_pets": False,
        "money": 100.0,
        "encoded": "hola",
        "height": 184,
    }

    user = User(**data)
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data_json)

    data = {
        "name": None,
        "age": 20,
        "has_pets": False,
        "money": None,
        "encoded": None,
        "height": None,
    }

    user = User()
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data)


def test_float32_primitive_type():
    class User(AvroBaseModel):
        height: Optional[types.Float32] = None

    data = {"height": 178.3}

    user = User(**data)
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    # Floating point error expected
    res = user.deserialize(avro_binary, create_instance=False)
    assert res["height"] != data["height"]
    assert math.isclose(res["height"], data["height"], abs_tol=1e-5)

    res = user.deserialize(avro_json, serialization_type="avro-json", create_instance=False)
    assert res["height"] == data["height"]

    # Floating point error expected
    res = user.deserialize(avro_binary)
    assert res.height != user.height
    assert math.isclose(res.height, user.height, abs_tol=1e-5)

    res = user.deserialize(avro_json, serialization_type="avro-json")
    assert res.height == user.height

    res = user.to_dict()
    assert res["height"] == data["height"]

    data = {"height": None}

    user = User()
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
