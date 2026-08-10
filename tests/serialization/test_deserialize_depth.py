import typing

import pytest

from dataclasses_avroschema import serialization


def nested_payload(depth: int) -> typing.Any:
    data: typing.Any = {"leaf": 1}
    for _ in range(depth):
        data = {"nested": data}

    return data


def test_an_ordinary_payload_is_normalised_as_before() -> None:
    data = {"name": "marcos", "pets": [{"name": "dog"}, {"name": "cat"}]}

    assert serialization.deserialize_from_context(data=data, context={}) == data


def test_a_payload_nested_past_the_maximum_is_refused() -> None:
    """A recursive schema lets the payload choose the depth, and the walk used to run until
    the interpreter stopped it with a `RecursionError`."""
    data = nested_payload(serialization.MAX_DESERIALIZE_DEPTH + 50)

    with pytest.raises(ValueError, match="nested more than"):
        serialization.deserialize_from_context(data=data, context={})


def test_a_payload_at_the_maximum_is_accepted() -> None:
    data = nested_payload(serialization.MAX_DESERIALIZE_DEPTH - 1)

    assert serialization.deserialize_from_context(data=data, context={}) == data


def test_lists_count_towards_the_depth() -> None:
    data: typing.Any = 1
    for _ in range(serialization.MAX_DESERIALIZE_DEPTH + 50):
        data = [data]

    with pytest.raises(ValueError, match="nested more than"):
        serialization.deserialize_from_context(data=data, context={})


def test_records_inside_unions_count_towards_the_depth() -> None:
    """A record reached through a union is walked by `sanitize_union`, which comes back
    here, so that path has to be counted as well."""
    data: typing.Any = {"leaf": 1}
    for _ in range(serialization.MAX_DESERIALIZE_DEPTH):
        data = {"nested": ("Record", data)}

    with pytest.raises(ValueError, match="nested more than"):
        serialization.deserialize_from_context(data=data, context={})
