import pytest
from pydantic import Field, conint
from pydantic.error_wrappers import ValidationError

from dataclasses_avroschema.avrodantic import AvroBaseModel


def test_int_constrained_type_serialize():
    class ConstrainedType(AvroBaseModel):
        value: conint(gt=0)

    c = ConstrainedType(value=1)
    serialized = c.serialize(serialization_type="avro-json")
    assert serialized == b'{"value": 1}'


def test_int_constrained_type_deserialize():
    class ConstrainedType(AvroBaseModel):
        value: conint(gt=0)

    ConstrainedType.deserialize(b'{"value": 1}', serialization_type="avro-json")


def test_int_constrained_type_deserialize_invalid():
    class ConstrainedType(AvroBaseModel):
        value: int = Field(gt=0)

    with pytest.raises(ValidationError):
        ConstrainedType.deserialize(b'{"value": 0}', serialization_type="avro-json")
