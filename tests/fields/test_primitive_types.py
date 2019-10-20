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

LIST_TYPE_AND_ITEMS_TYPE = (
    (str, "string"),
    (int, "int"),
    (bool, "boolean"),
    (float, "float"),
    (bytes, "bytes"),
)


@pytest.mark.parametrize("inmutable_type", fields.PYTHON_INMUTABLE_TYPES)
def test_inmutable_types(inmutable_type):
    name = "a_field"
    field = fields.Field(name, inmutable_type, dataclasses.MISSING)
    avro_type = fields.PYTHON_TYPE_TO_AVRO[inmutable_type]

    assert {"name": name, "type": avro_type} == field.to_dict()


@pytest.mark.parametrize("inmutable_type", fields.PYTHON_INMUTABLE_TYPES)
def test_inmutable_types_with_default_value_none(inmutable_type):
    name = "a_field"
    field = fields.Field(name, inmutable_type, None)
    avro_type = [fields.NULL, fields.PYTHON_TYPE_TO_AVRO[inmutable_type]]

    assert {"name": name, "type": avro_type, "default": fields.NULL} == field.to_dict()


@pytest.mark.parametrize("inmutable_type,default", PRIMITIVE_TYPES_AND_DEFAULTS)
def test_inmutable_types_with_default_value(inmutable_type, default):
    name = "a_field"
    field = fields.Field(name, inmutable_type, default)
    avro_type = [fields.PYTHON_TYPE_TO_AVRO[inmutable_type], fields.NULL]

    assert {"name": name, "type": avro_type, "default": default} == field.to_dict()
