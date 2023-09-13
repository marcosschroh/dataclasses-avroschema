import pytest
from pydantic import Field, conint
from pydantic.error_wrappers import ValidationError

from dataclasses_avroschema.avrodantic import AvroBaseModel
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

    with pytest.raises(ValidationError):
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
