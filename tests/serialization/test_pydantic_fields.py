import pytest
from pydantic import Field
from pydantic.error_wrappers import ValidationError

from dataclasses_avroschema.avrodantic import AvroBaseModel


def test_int_constraint_type_serialize():
    class ConstraintType(AvroBaseModel):
        value: int = Field(gt=0)

    c = ConstraintType(value=1)
    serialized = c.serialize(serialization_type="avro-json")
    assert serialized == b'{"value": 1}'


def test_int_constraint_type_deserialize():
    class ConstraintType(AvroBaseModel):
        value: int = Field(gt=0)

    ConstraintType.deserialize(b'{"value": 1}', serialization_type="avro-json")


def test_int_constraint_type_deserialize_invalid():
    class ConstraintType(AvroBaseModel):
        value: int = Field(gt=0)

    with pytest.raises(ValidationError):
        ConstraintType.deserialize(b'{"value": 0}', serialization_type="avro-json")
