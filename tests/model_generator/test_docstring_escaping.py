"""
A record `doc` is copied into the docstring of the generated class. The schema is not
necessarily written by the person running the generator, so the value must not be able
to close the docstring: everything after the closing delimiter would be parsed as code
and would run when the generated module is imported.
"""

import ast
import inspect
import typing

import pytest

from dataclasses_avroschema import ModelGenerator, ModelType

# Closes the docstring, runs a statement, then reopens one so the rest of the
# generated class body stays syntactically valid.
BREAKOUT = '"""\nINJECTED = 1\n"""'

# A `doc` that ends in a backslash escapes the closing delimiter instead.
TRAILING_BACKSLASH = "ends with a backslash \\"

# Four quotes in a row survive an escape that only rewrites the first three.
QUOTE_RUN = '""""\nINJECTED = 1\n""""'


def render(schema: typing.Dict[str, typing.Any]) -> str:
    return ModelGenerator().render(schema=schema, model_type=ModelType.AVRODANTIC.value)


def module_of(source: str) -> ast.Module:
    """The generated source parses -- a failure here is the trailing backslash case."""
    return ast.parse(source)


@pytest.mark.parametrize("payload", [BREAKOUT, QUOTE_RUN, TRAILING_BACKSLASH])
def test_record_doc_cannot_escape_the_docstring(payload: str) -> None:
    tree = module_of(
        render(
            {
                "type": "record",
                "name": "User",
                "doc": payload,
                "fields": [{"name": "name", "type": "string"}],
            }
        )
    )

    injected = [node for node in ast.walk(tree) if isinstance(node, ast.Name) and node.id == "INJECTED"]
    assert not injected, "schema doc became code"


@pytest.mark.parametrize("payload", [BREAKOUT, QUOTE_RUN, TRAILING_BACKSLASH])
def test_enum_doc_cannot_escape_the_docstring(payload: str) -> None:
    tree = module_of(
        render(
            {
                "type": "record",
                "name": "User",
                "fields": [
                    {
                        "name": "favorite_colour",
                        "type": {"type": "enum", "name": "Colour", "symbols": ["BLUE"], "doc": payload},
                    }
                ],
            }
        )
    )

    injected = [node for node in ast.walk(tree) if isinstance(node, ast.Name) and node.id == "INJECTED"]
    assert not injected, "schema doc became code"


@pytest.mark.parametrize("payload", [BREAKOUT, QUOTE_RUN, TRAILING_BACKSLASH, "An User", "Peter's Address"])
def test_docstring_value_survives_escaping(payload: str) -> None:
    """Escaping changes the source, never the docstring the generated class ends up with."""
    source = render(
        {
            "type": "record",
            "name": "User",
            "doc": payload,
            "fields": [{"name": "name", "type": "string"}],
        }
    )

    namespace: typing.Dict[str, typing.Any] = {}
    exec(compile(source, "<generated>", "exec"), namespace)  # noqa: S102

    # `cleandoc` removes the indentation the generator adds; the text must be identical.
    assert inspect.cleandoc(namespace["User"].__doc__) == inspect.cleandoc(payload)


def test_escaping_leaves_ordinary_docs_untouched() -> None:
    from dataclasses_avroschema.model_generator.lang.python.base import escape_docstring

    for value in ("An User", "An Address", "Peter's Address", "line one\nline two", "café"):
        assert escape_docstring(value) == value
