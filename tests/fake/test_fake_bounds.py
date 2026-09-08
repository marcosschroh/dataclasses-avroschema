import dataclasses
import decimal

import pytest

from dataclasses_avroschema import AvroModel, types
from dataclasses_avroschema.fields import fields


def test_a_fixed_field_of_ordinary_size_is_faked() -> None:
    @dataclasses.dataclass
    class User(AvroModel):
        md5: types.confixed(size=16)  # type: ignore[valid-type]

    assert len(User.fake().md5) == 16


def test_a_fixed_field_above_the_maximum_is_refused() -> None:
    @dataclasses.dataclass
    class User(AvroModel):
        md5: types.confixed(size=fields.MAX_FAKE_FIXED_SIZE + 1)  # type: ignore[valid-type]

    with pytest.raises(ValueError, match="above the maximum"):
        User.fake()


def test_a_fixed_field_at_the_maximum_is_faked() -> None:
    @dataclasses.dataclass
    class User(AvroModel):
        md5: types.confixed(size=fields.MAX_FAKE_FIXED_SIZE)  # type: ignore[valid-type]

    assert len(User.fake().md5) == fields.MAX_FAKE_FIXED_SIZE


def test_a_decimal_field_of_ordinary_size_is_faked() -> None:
    @dataclasses.dataclass
    class User(AvroModel):
        score: types.condecimal(max_digits=11, decimal_places=5)  # type: ignore[valid-type]

    assert isinstance(User.fake().score, decimal.Decimal)


def test_a_decimal_field_above_the_maximum_is_refused() -> None:
    @dataclasses.dataclass
    class User(AvroModel):
        score: types.condecimal(  # type: ignore[valid-type]
            max_digits=fields.MAX_FAKE_DECIMAL_DIGITS + 1, decimal_places=2
        )

    with pytest.raises(ValueError, match="above the maximum"):
        User.fake()


def test_a_decimal_field_at_the_maximum_is_faked() -> None:
    @dataclasses.dataclass
    class User(AvroModel):
        score: types.condecimal(  # type: ignore[valid-type]
            max_digits=fields.MAX_FAKE_DECIMAL_DIGITS, decimal_places=2
        )

    assert isinstance(User.fake().score, decimal.Decimal)


def test_the_schema_is_unaffected_by_the_bound() -> None:
    """The limit belongs to `fake()` only: a model with a large `fixed` still serialises and
    still produces the same avro schema."""

    @dataclasses.dataclass
    class User(AvroModel):
        md5: types.confixed(size=fields.MAX_FAKE_FIXED_SIZE + 1)  # type: ignore[valid-type]

    assert User.avro_schema_to_python()["fields"][0]["type"]["size"] == fields.MAX_FAKE_FIXED_SIZE + 1
