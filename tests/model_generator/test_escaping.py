"""
The generator writes values taken from the schema into the Python source it emits.
The schema is not necessarily written by the person running the generator, so a value
must never be able to close the literal it is rendered into: everything after the
closing quote would be parsed as code and would run when the generated module is
imported.

Each test below renders a hostile value, parses the result, and asserts that the
marker the value tried to smuggle in is *not* part of the module's syntax tree.
"""

import ast
import json
import typing

import pytest

from dataclasses_avroschema import ModelGenerator, ModelType
from dataclasses_avroschema.model_generator.lang.python.base import EnumRepresentation

# Closes a double quoted literal, starts a statement, then reopens a literal so the
# rest of the generated line stays syntactically valid.
BREAKOUT = 'x"\nINJECTED = 1\nFILLER = "y'

# Same idea for a value rendered into a single quoted literal.
BREAKOUT_SINGLE = "x'\nINJECTED = 1\nFILLER = 'y"


def assert_not_injected(source: str) -> None:
    """The module parses, and `INJECTED` is not a name anywhere in it."""
    tree = ast.parse(source)
    injected = [
        node
        for node in ast.walk(tree)
        if (isinstance(node, ast.Name) and node.id == "INJECTED")
        or (isinstance(node, ast.keyword) and node.arg == "INJECTED")
    ]
    assert not injected, f"schema value became code:\n{source}"


def render(schema: typing.Dict[str, typing.Any], model_type: str = ModelType.AVRODANTIC.value) -> str:
    return ModelGenerator().render(schema=schema, model_type=model_type)


@pytest.mark.parametrize("payload", [BREAKOUT, BREAKOUT_SINGLE])
@pytest.mark.parametrize("avro_type", ["string", "bytes"])
def test_field_default_cannot_escape_its_literal(payload: str, avro_type: str) -> None:
    assert_not_injected(
        render(
            {
                "type": "record",
                "name": "User",
                "fields": [{"name": "nickname", "type": avro_type, "default": payload}],
            }
        )
    )


@pytest.mark.parametrize("payload", [BREAKOUT, BREAKOUT_SINGLE])
def test_namespace_cannot_escape_its_meta_literal(payload: str) -> None:
    assert_not_injected(
        render(
            {
                "type": "record",
                "name": "User",
                "namespace": payload,
                "fields": [{"name": "name", "type": "string"}],
            }
        )
    )


@pytest.mark.parametrize("payload", [BREAKOUT, BREAKOUT_SINGLE])
def test_schema_name_cannot_escape_its_meta_literal(payload: str) -> None:
    # A schema name that is not a valid class name is rendered into Meta.schema_name
    # so the original is preserved.
    assert_not_injected(
        render(
            {
                "type": "record",
                "name": payload,
                "fields": [{"name": "name", "type": "string"}],
            }
        )
    )


@pytest.mark.parametrize("payload", [BREAKOUT, BREAKOUT_SINGLE])
def test_enum_symbol_value_is_escaped(payload: str) -> None:
    """
    Asserted on `render_symbols` rather than through a schema, because a symbol like this
    is rejected before rendering: by `fastavro.parse_schema` on the public path, and by
    the generator's own name check. The escaping is the layer underneath those, and it is
    what keeps the value side safe if a symbol ever reaches it.

    Only the value half is covered. A symbol is also rendered as the enum member *name*,
    which is an identifier rather than a literal and cannot be made safe by escaping.
    """
    representation = EnumRepresentation(
        name="Colour",
        schema={"type": "enum", "name": "Colour", "symbols": ["BLUE", payload]},
        base_class="",
        symbols={"BLUE": "BLUE", "HOSTILE": payload},
    )

    assert json.dumps(payload) in representation.render_symbols()


@pytest.mark.parametrize("payload", [BREAKOUT, BREAKOUT_SINGLE])
def test_field_doc_cannot_escape_pydantic_description(payload: str) -> None:
    assert_not_injected(
        render(
            {
                "type": "record",
                "name": "User",
                "fields": [{"name": "name", "type": "string", "doc": payload}],
            }
        )
    )


def test_escaping_leaves_ordinary_values_untouched() -> None:
    """The escape must not change what is generated for values with nothing to escape."""
    from dataclasses_avroschema.model_generator.lang.python.base import escape_string

    for value in ("marcos", "some.name.space", "u00ffffffffffffx", "café", 10, True):
        assert escape_string(value) == str(value)
