import dataclasses
import io

import fastavro

from dataclasses_avroschema import AvroModel
from dataclasses_avroschema.serialization import deserialize
from dataclasses_avroschema.utils import get_klass_annotations


@dataclasses.dataclass
class Nested(AvroModel):
    n: str = "n"


@dataclasses.dataclass
class Mixin:
    inner: Nested = dataclasses.field(default_factory=Nested)


@dataclasses.dataclass
class Model(AvroModel, Mixin):
    own: str = "y"


def test_asdict_resolves_a_field_inherited_from_a_mixin() -> None:
    """
    `standardize_custom_type` reads the model's own `__annotations__` and only falls back
    to `get_type_hints` when the model does not subclass the base class directly. A model
    that subclasses it directly *and* takes a field from a mixin skipped that fallback and
    raised `KeyError`.
    """
    assert Model.mro()[1] is AvroModel

    assert Model().asdict() == {"own": "y", "inner": {"n": "n"}}


def test_asdict_does_not_write_into_the_class_annotations() -> None:
    """The fallback used to merge the resolved hints into the class's own dict."""
    before = dict(get_klass_annotations(Model))

    Model().asdict()

    assert dict(get_klass_annotations(Model)) == before


def test_avro_json_deserialize_reads_only_the_first_record() -> None:
    """
    Only the first record is returned, so the rest must not be parsed. This checks the
    behaviour rather than the timing: a later record that does not satisfy the schema
    used to raise `ValueError`, which it could only do if every record were read.
    """
    schema = {"type": "record", "name": "R", "fields": [{"name": "a", "type": "string"}]}

    output = io.StringIO()
    fastavro.json_writer(output, schema, [{"a": "first"}])
    data = output.getvalue().encode() + b'\n{"b": 1}\n'

    assert deserialize(data=data, schema=schema, serialization_type="avro-json") == {"a": "first"}
