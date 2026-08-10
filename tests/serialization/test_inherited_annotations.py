import dataclasses

from dataclasses_avroschema import AvroModel
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
