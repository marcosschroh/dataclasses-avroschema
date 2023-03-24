import dataclasses
import typing

import pytest

from dataclasses_avroschema import field_utils, fields

from . import consts


@pytest.mark.parametrize("primitive_type", field_utils.PYTHON_INMUTABLE_TYPES)
def test_primitive_types(primitive_type):
    name = "a_field"
    field = fields.AvroField(name, primitive_type, default=dataclasses.MISSING)

    assert {"name": name, "type": field.avro_type} == field.to_dict()


@pytest.mark.parametrize("primitive_type", field_utils.PYTHON_INMUTABLE_TYPES)
def test_primitive_types_with_default_value_none(primitive_type):
    name = "a_field"
    field = fields.AvroField(name, primitive_type, default=None)
    avro_type = [field_utils.NULL, field.avro_type]

    assert {"name": name, "type": avro_type, "default": None} == field.to_dict()


@pytest.mark.parametrize("primitive_type,default", consts.PRIMITIVE_TYPES_AND_DEFAULTS)
def test_primitive_types_with_default_value(primitive_type, default):
    name = "a_field"
    field = fields.AvroField(name, primitive_type, default=default)

    if field.avro_type == field_utils.BYTES:
        default = default.decode()

    assert {"name": name, "type": field.avro_type, "default": default} == field.to_dict()


@pytest.mark.parametrize("primitive_type,invalid_default", consts.PRIMITIVE_TYPES_AND_INVALID_DEFAULTS)
def test_invalid_default_values(primitive_type, invalid_default):
    name = "a_field"
    field = fields.AvroField(name, primitive_type, default=invalid_default)

    msg = f"Invalid default type. Default should be {primitive_type}"
    with pytest.raises(AssertionError, match=msg):
        field.to_dict()


def test_invalid_type():
    msg = f"Type {typing.Any} is unknown. Please check the valid types at https://marcosschroh.github.io/dataclasses-avroschema/fields_specification/#avro-field-and-python-types-summary"  # noqa
    with pytest.raises(ValueError, match=msg):
        name = "a_field"
        fields.AvroField(name, typing.Any)
