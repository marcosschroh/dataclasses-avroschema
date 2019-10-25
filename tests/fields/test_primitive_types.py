import pytest
import dataclasses

from dataclasses_avroschema import fields


PRIMITIVE_TYPES_AND_DEFAULTS = (
    (str, "test"),
    (int, 1),
    (bool, True),
    (float, 10.4),
    # (bytes, "test".encode()),
)

PRIMITIVE_TYPES_AND_INVALID_DEFAULTS = (
    (str, 1),
    (int, "test"),
    (bool, 10),
    (float, False),
    # (bytes, "test".encode()),
)


LIST_TYPE_AND_ITEMS_TYPE = (
    (str, "string"),
    (int, "int"),
    (bool, "boolean"),
    (float, "float"),
    (bytes, "bytes"),
)


@pytest.mark.parametrize("primitive_type", fields.PYTHON_INMUTABLE_TYPES)
def test_primitive_types(primitive_type):
    name = "a_field"
    field = fields.Field(name, primitive_type, dataclasses.MISSING)
    avro_type = fields.PYTHON_TYPE_TO_AVRO[primitive_type]

    assert {"name": name, "type": avro_type} == field.to_dict()


@pytest.mark.parametrize("primitive_type", fields.PYTHON_INMUTABLE_TYPES)
def test_primitive_types_with_default_value_none(primitive_type):
    name = "a_field"
    field = fields.Field(name, primitive_type, None)
    avro_type = [fields.NULL, fields.PYTHON_TYPE_TO_AVRO[primitive_type]]

    assert {"name": name, "type": avro_type, "default": fields.NULL} == field.to_dict()


@pytest.mark.parametrize("primitive_type,default", PRIMITIVE_TYPES_AND_DEFAULTS)
def test_primitive_types_with_default_value(primitive_type, default):
    name = "a_field"
    field = fields.Field(name, primitive_type, default)
    avro_type = [fields.PYTHON_TYPE_TO_AVRO[primitive_type], fields.NULL]

    assert {"name": name, "type": avro_type, "default": default} == field.to_dict()


@pytest.mark.parametrize(
    "primitive_type,invalid_default", PRIMITIVE_TYPES_AND_INVALID_DEFAULTS
)
def test_invalid_default_values(primitive_type, invalid_default):
    name = "a_field"
    field = fields.Field(name, primitive_type, invalid_default)

    msg = f"Invalid default type. Default should be {primitive_type}"
    with pytest.raises(AssertionError, match=msg):
        field.to_dict()
