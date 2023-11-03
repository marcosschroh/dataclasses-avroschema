import json
import math

import pytest
from pydantic import Field, conint
from pydantic.v1.error_wrappers import ValidationError

from dataclasses_avroschema import types
from dataclasses_avroschema.pydantic.v1.main import AvroBaseModel
from dataclasses_avroschema.schema_generator import AVRO, AVRO_JSON


class CustomClass:
    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, CustomClass):
            return value
        elif not isinstance(value, str):
            raise ValueError(f"Value must be a string or CustomClass - not {type(value)}")

        return cls(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CustomClass):
            return NotImplemented

        return self.value == other.value

    def __str__(self) -> str:
        return f"{self.value}"


class Parent(AvroBaseModel):
    custom_class: CustomClass

    class Config:
        json_encoders = {CustomClass: str}


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

    with pytest.raises(AssertionError):
        ConstrainedType.deserialize(b'{"value": 0}', serialization_type="avro-json")


@pytest.mark.parametrize(
    "serialization_type, expected_result", [(AVRO, parent_avro_binary), (AVRO_JSON, parent_avro_json)]
)
def test_custom_class_type_serialize(serialization_type: str, expected_result: bytes):
    serialized = parent_under_test.serialize(serialization_type)
    assert serialized == expected_result


@pytest.mark.parametrize("serialization_type, data", [(AVRO, parent_avro_binary), (AVRO_JSON, parent_avro_json)])
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

    data = {"name": "marcos", "age": 20, "has_pets": False, "money": 100.0, "encoded": b"hola", "height": 184}
    data_json = {"name": "marcos", "age": 20, "has_pets": False, "money": 100.0, "encoded": "hola", "height": 184}

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

    data = {"name": "Juan", "age": 30, "has_pets": False, "money": 100.0, "encoded": b"hola", "height": 184}
    data_json = {"name": "Juan", "age": 30, "has_pets": False, "money": 100.0, "encoded": "hola", "height": 184}

    # assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    # assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user
    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data_json)


def test_primitive_types_with_nulls():
    class User(AvroBaseModel):
        name: str = None
        age: int = 20
        has_pets: bool = False
        money: float = None
        encoded: bytes = None
        height: types.Int32 = None

    data = {"name": None, "age": 20, "has_pets": False, "money": 100.0, "encoded": b"hola", "height": 184}
    data_json = {"name": None, "age": 20, "has_pets": False, "money": 100.0, "encoded": "hola", "height": 184}

    user = User(**data)
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data_json)

    data = {"name": None, "age": 20, "has_pets": False, "money": None, "encoded": None, "height": None}

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
        height: types.Float32 = None

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
