import dataclasses

import pytest

from dataclasses_avroschema import AvroField
from dataclasses_avroschema.pydantic.v1 import AvroBaseModel

from . import consts


class PydanticCustomClass:
    @classmethod
    def __get_validators__(cls):
        pass  # This is a stub method

    @classmethod
    def validate(cls):
        pass  # This is a stub method too


class PydanticCustomClassParent(AvroBaseModel):
    class Config:
        json_encoders = {PydanticCustomClass: str}


def test_pydantic_custom_class_field():
    field_name = "custom_class"
    custom_class_field = AvroField(field_name, PydanticCustomClass, PydanticCustomClassParent)

    assert custom_class_field.to_dict() == {
        "type": "string",
        "name": field_name,
    }


def test_pydantic_custom_class_field_with_default():
    field_name = "custom_class"
    default = "a default string"
    custom_class_field = AvroField(
        field_name,
        PydanticCustomClass,
        PydanticCustomClassParent,
        default=default,
    )

    assert custom_class_field.to_dict() == {
        "type": "string",
        "name": field_name,
        "default": default,
    }


def test_pydantic_custom_class_field_with_default_factory():
    """
    When the type is pydantic custom class, the default_factory should
    be omitted
    """
    field_name = "custom_class"
    custom_class_field = AvroField(
        field_name,
        PydanticCustomClass,
        PydanticCustomClassParent,
        default_factory=int,
    )

    assert custom_class_field.default_factory is dataclasses.MISSING


def test_pydantic_custom_class_field_with_misconfigured_parent():
    class MisconfiguredParent(AvroBaseModel):
        pass

    field_name = "custom_class"
    with pytest.raises(ValueError):
        AvroField(field_name, PydanticCustomClass, MisconfiguredParent)


@pytest.mark.parametrize("python_type,avro_type", consts.PYDANTIC_V1_LOGICAL_TYPES)
def test_logical_types(python_type, avro_type):
    name = "a logical type"
    python_type = python_type
    field = AvroField(name, python_type)

    expected = {"name": name, "type": avro_type}

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_type,avro_type", consts.PYDANTIC_V1_LOGICAL_TYPES)
def test_logical_types_with_null_as_default(python_type, avro_type):
    name = "a logical type"
    field = AvroField(name, python_type, default=None)

    expected = {
        "name": name,
        "type": ["null", avro_type],
        "default": None,
    }

    assert expected == field.to_dict()
