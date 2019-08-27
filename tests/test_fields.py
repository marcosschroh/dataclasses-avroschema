import pytest
import dataclasses
import typing

from dataclasses_schema_generator import fields


INMUTABLE_TYPES_AND_DEFAULTS = (
    (str, "test"),
    (int, 1),
    (bool, True),
    (float, 10.4),
)


def test_invalid_type_field():
    python_type = typing.Set
    name = "test_field"
    msg = f"Invalid Type for field {name}. Accepted types are list, tuple or dict"

    with pytest.raises(ValueError, match=msg):
        fields.Field(name, python_type, dataclasses.MISSING)


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


@pytest.mark.parametrize("inmutable_type,default", INMUTABLE_TYPES_AND_DEFAULTS)
def test_inmutable_types_with_default_value(inmutable_type, default):
    name = "a_field"
    field = fields.Field(name, inmutable_type, default)
    avro_type = [fields.PYTHON_TYPE_TO_AVRO[inmutable_type], fields.NULL]

    assert {"name": name, "type": avro_type, "default": default} == field.to_dict()


def test_container_types():
    pass
