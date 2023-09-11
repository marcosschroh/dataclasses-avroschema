import pytest
from pydantic import Field, conint
from pydantic.error_wrappers import ValidationError

from dataclasses_avroschema.avrodantic import AvroBaseModel


class GenericClass:
    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, GenericClass):
            return value
        elif not isinstance(value, str):
            raise ValueError(f"Value must be a string or GenericClass - not {type(value)}")

        return cls(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GenericClass):
            return NotImplemented

        return self.value == other.value

    def __str__(self) -> str:
        return f"{self.value}"


class Parent(AvroBaseModel):
    generic_class: GenericClass

    class Config:
        json_encoders = {GenericClass: str}


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


def test_generic_class_type_serialize():
    obj_under_test = Parent(generic_class=GenericClass("gclass value"))

    serialized = obj_under_test.serialize(serialization_type="avro-json")
    assert serialized == b'{"generic_class": "gclass value"}'


def test_generic_class_type_deserialize():
    expected = Parent(generic_class=GenericClass("gclass value"))

    deserialized = Parent.deserialize(b'{"generic_class": "gclass value"}', serialization_type="avro-json")
    assert deserialized == expected


def test_generic_class_deserialize_invalid():
    with pytest.raises(ValidationError):
        Parent.deserialize(b'{"generic_class": 1}', serialization_type="avro-json")
