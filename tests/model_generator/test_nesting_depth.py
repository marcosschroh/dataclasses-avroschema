import typing

import pytest

from dataclasses_avroschema import ModelGenerator, ModelType, types
from dataclasses_avroschema.model_generator.lang.python import base


def nested_array_schema(depth: int) -> types.JsonDict:
    """A record whose single field is `depth` arrays deep."""
    field_type: typing.Any = "string"
    for _ in range(depth):
        field_type = {"type": "array", "items": field_type}

    return {
        "type": "record",
        "name": "Deep",
        "fields": [{"name": "nested", "type": field_type}],
    }


def test_an_ordinary_schema_still_renders() -> None:
    result = ModelGenerator().render(schema=nested_array_schema(3), model_type=ModelType.DATACLASS.value)

    assert "typing.List[typing.List[typing.List[str]]]" in result


def test_a_schema_nested_past_the_maximum_is_refused() -> None:
    schema = nested_array_schema(base.MAX_NESTING_DEPTH + 50)

    with pytest.raises(ValueError, match="nested more than"):
        ModelGenerator().render(schema=schema, model_type=ModelType.DATACLASS.value)


def test_the_maximum_can_be_raised_on_the_generator() -> None:
    depth = base.MAX_NESTING_DEPTH + 50
    model_generator = ModelGenerator()
    generator = model_generator.model_type_mapper[ModelType.DATACLASS.value]
    generator.max_nesting_depth = depth + 10

    result = model_generator.render(schema=nested_array_schema(depth), model_type=ModelType.DATACLASS.value)

    assert result.count("typing.List") == depth


def test_the_depth_is_released_between_renders() -> None:
    """The counter lives on the generator, and generators are reused, so it has to unwind
    even when a render fails."""
    model_generator = ModelGenerator()

    with pytest.raises(ValueError, match="nested more than"):
        model_generator.render(
            schema=nested_array_schema(base.MAX_NESTING_DEPTH + 50), model_type=ModelType.DATACLASS.value
        )

    generator = model_generator.model_type_mapper[ModelType.DATACLASS.value]
    assert generator._nesting_depth == 0
