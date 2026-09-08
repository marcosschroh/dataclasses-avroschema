import decimal

import pytest

from dataclasses_avroschema import serialization


def test_a_decimal_round_trips_unchanged() -> None:
    value = decimal.Decimal("3.14")

    encoded = serialization.decimal_to_str(value, precision=3, scale=2)

    assert serialization.string_to_decimal(value=encoded, schema={"precision": 3, "scale": 2}) == value


def test_the_module_level_context_is_left_alone() -> None:
    """`decimal_context` is shared, so writing the schema's precision into it changed the
    precision of unrelated decimal work elsewhere in the process."""
    before = serialization.decimal_context.prec

    serialization.string_to_decimal(value="0141", schema={"precision": 5, "scale": 2})

    assert serialization.decimal_context.prec == before


def test_precision_above_the_maximum_is_rejected() -> None:
    schema = {"precision": serialization.MAX_DECIMAL_PRECISION + 1, "scale": 1}

    with pytest.raises(ValueError, match="above the maximum"):
        serialization.string_to_decimal(value="01" * 8, schema=schema)


def test_precision_at_the_maximum_is_accepted() -> None:
    schema = {"precision": serialization.MAX_DECIMAL_PRECISION, "scale": 0}

    assert serialization.string_to_decimal(value="01", schema=schema) == decimal.Decimal(1)


@pytest.mark.parametrize("precision", [0, -1, 3.5, "3", True, None])
def test_a_precision_that_is_not_a_positive_integer_is_rejected(precision) -> None:
    with pytest.raises(ValueError, match="must be a positive integer"):
        serialization.string_to_decimal(value="01", schema={"precision": precision, "scale": 0})


@pytest.mark.parametrize("scale", [-1, 4, 1.5, "1", True, None])
def test_a_scale_outside_the_precision_is_rejected(scale) -> None:
    with pytest.raises(ValueError, match="`scale` must be an integer"):
        serialization.string_to_decimal(value="01", schema={"precision": 3, "scale": scale})


def test_a_payload_larger_than_the_precision_allows_is_rejected() -> None:
    """The hex payload is schema-controlled too, and the cost of decoding it grows with its
    length, so a value that cannot fit in the declared digits is refused up front."""
    schema = {"precision": 3, "scale": 0}

    with pytest.raises(ValueError, match="does not fit in the 3 digits"):
        serialization.string_to_decimal(value="01" * 64, schema=schema)


def test_the_payload_bound_accepts_everything_the_writer_produces() -> None:
    """`prepare_bytes_decimal` scales the unscaled value up before encoding, so the bound
    has to leave room for that."""
    precision, scale = 9, 4
    value = decimal.Decimal("12345.6789")

    encoded = serialization.decimal_to_str(value, precision=precision, scale=scale)

    assert serialization.string_to_decimal(value=encoded, schema={"precision": precision, "scale": scale}) == value


@pytest.mark.parametrize(("precision", "scale"), [(1, 0), (3, 2), (9, 4), (18, 6), (38, 10)])
def test_max_decimal_bytes_matches_the_writer(precision: int, scale: int) -> None:
    """The largest value the writer can emit for these settings must fit inside the bound."""
    digits = decimal.Decimal(10) ** precision - 1
    value = digits.scaleb(-scale)

    encoded = serialization.decimal_to_str(value, precision=precision, scale=scale)

    assert len(bytes.fromhex(encoded.replace(r"\u", ""))) <= serialization.max_decimal_bytes(
        precision=precision, scale=scale
    )
