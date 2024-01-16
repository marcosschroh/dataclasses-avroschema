import dataclasses
from typing import Any

import pytest
from pydantic import ConfigDict, GetCoreSchemaHandler, field_serializer
from pydantic_core import CoreSchema, core_schema

from dataclasses_avroschema import AvroField
from dataclasses_avroschema.pydantic import AvroBaseModel

from . import consts


class PydanticCustomType:
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class MyModel(AvroBaseModel):
    model_config = ConfigDict(json_encoders={PydanticCustomType: str})
    x: PydanticCustomType

    @field_serializer("x")
    def serialize_x(self, x: PydanticCustomType, _info):
        return str(x)


def test_pydantic_custom_class_field():
    field_name = "custom_class"
    custom_class_field = AvroField(field_name, PydanticCustomType, MyModel)

    assert custom_class_field.to_dict() == {
        "type": "string",
        "name": field_name,
    }


def test_pydantic_custom_class_field_with_default():
    field_name = "custom_class"
    default = "a default string"
    custom_class_field = AvroField(
        field_name,
        PydanticCustomType,
        MyModel,
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
        PydanticCustomType,
        MyModel,
        default_factory=int,
    )

    assert custom_class_field.default_factory is dataclasses.MISSING


def test_pydantic_custom_class_field_with_misconfigured_parent():
    class MisconfiguredParent(AvroBaseModel):
        pass

    field_name = "custom_class"
    with pytest.raises(KeyError):
        AvroField(field_name, PydanticCustomType, MisconfiguredParent)


@pytest.mark.parametrize("python_type,avro_type", consts.PYDANTIC_LOGICAL_TYPES)
def test_logical_types(python_type, avro_type):
    name = "a logical type"
    field = AvroField(name, python_type)

    expected = {"name": name, "type": avro_type}

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_type,avro_type", consts.PYDANTIC_LOGICAL_TYPES)
def test_logical_types_with_null_as_default(python_type, avro_type):
    name = "a logical type"
    field = AvroField(name, python_type, default=None)

    expected = {
        "name": name,
        "type": ["null", avro_type],
        "default": None,
    }

    assert expected == field.to_dict()
