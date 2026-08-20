"""
Some schema values are rendered into the generated source as code rather than as text:
a record name in callable position, a namespace inside an annotation, an enum member
name, a `pydantic-class` annotation. Escaping does not apply to those -- the value is
meant to be evaluated -- so a schema that does not supply a name is refused.
"""

import re
import typing

import pytest

from dataclasses_avroschema import ModelGenerator, ModelType
from dataclasses_avroschema.exceptions import InvalidSchemaValue
from dataclasses_avroschema.model_generator.lang.python.dataclasses.dataclass_model_generator import (
    DataclassModelGenerator,
)

MARKER = "INJECTED"

A_NAME = "a name matching [A-Za-z_][A-Za-z0-9_]*"
A_TYPE = "a name, or a call to a name with literal arguments"


def refusal(location: str, rule: str) -> str:
    """
    The message the end user is shown, as a regular expression.

    The refused value sits between the two halves and is not matched on: it is the
    schema's own payload, so it carries whatever characters the schema author chose.
    """
    return re.escape(f"Invalid {location}") + ".*" + re.escape(f"so it must be {rule}")


def render(schema: typing.Dict[str, typing.Any], model_type: str = ModelType.DATACLASS.value) -> str:
    return ModelGenerator().render(schema=schema, model_type=model_type)


def test_record_name_in_callable_position_is_refused() -> None:
    # `get_field_default` renders a referenced record name as `default_factory=lambda: <name>(...)`.
    payload = f"({MARKER}() or (lambda **kw: None))"
    schema = {
        "type": "record",
        "name": "Foo",
        "fields": [
            {"name": "a", "type": {"type": "record", "name": payload, "fields": [{"name": "x", "type": "string"}]}},
            {"name": "b", "type": payload, "default": {"x": "hi"}},
        ],
    }

    with pytest.raises(InvalidSchemaValue, match=refusal("record name", A_NAME)):
        render(schema)


def test_fixed_namespace_in_annotation_is_refused() -> None:
    payload = f'a") or {MARKER} or types.confixed(size=16, namespace="b'
    schema = {
        "type": "record",
        "name": "Attack",
        "fields": [{"name": "payload", "type": {"type": "fixed", "name": "MyFixed", "size": 16, "namespace": payload}}],
    }

    with pytest.raises(InvalidSchemaValue, match=refusal("namespace", f"a dot separated sequence of {A_NAME}")):
        render(schema)


def test_enum_default_outside_the_symbol_grammar_is_refused() -> None:
    # `casefy.uppercase` only case folds, so a newline survives into the class body.
    schema = {
        "type": "record",
        "name": "UserEvent",
        "fields": [
            {
                "name": "status",
                "type": {"type": "enum", "name": "Status", "symbols": ["ACTIVE", "INACTIVE"]},
                "default": f"ACTIVE\n{MARKER} = (4, 5, 6)\nFILLER = (7, 8, 9)",
            }
        ],
    }

    with pytest.raises(InvalidSchemaValue, match=refusal("enum default", A_NAME)):
        render(schema)


def test_enum_symbol_is_refused_on_the_unvalidated_generator_path() -> None:
    # `ModelGenerator.render` rejects this through `fastavro.parse_schema`; the generator
    # classes are importable and their `render` does not validate.
    schema = {
        "type": "record",
        "name": "User",
        "fields": [
            {
                "name": "favorite_colour",
                "type": {"type": "enum", "name": "Colour", "symbols": ["BLUE", f'X"\n{MARKER} = 1\nY = "z']},
            }
        ],
    }

    with pytest.raises(InvalidSchemaValue, match=refusal("enum symbol", A_NAME)):
        DataclassModelGenerator().render(schemas=[schema])


def test_aliases_given_as_a_string_are_refused() -> None:
    # A list is rendered through its `repr`, which quotes every entry. A bare string is not.
    schema = {
        "type": "record",
        "name": "Attack",
        "fields": [
            {"name": "payload", "type": {"type": "fixed", "name": "MyFixed", "size": 16, "aliases": f"X or {MARKER}"}}
        ],
    }

    with pytest.raises(InvalidSchemaValue, match=refusal("aliases", "a list")):
        render(schema)


@pytest.mark.parametrize(
    "payload",
    [
        f"EmailStr or {MARKER}",  # an operator reaches a second expression
        f"{MARKER}.attribute",  # an attribute lookup reaches an object graph
        'conint(gt=eval("1"))',  # a call in an argument position reaches the builtins
        "lambda: 1",
        "[x for x in ()]",
    ],
)
def test_pydantic_class_richer_than_a_constrained_type_is_refused(payload: str) -> None:
    schema = {
        "type": "record",
        "name": "User",
        "fields": [{"name": "email", "type": {"type": "string", "pydantic-class": payload}}],
    }

    for model_type in (ModelType.PYDANTIC.value, ModelType.AVRODANTIC.value):
        with pytest.raises(InvalidSchemaValue, match=refusal("pydantic-class", A_TYPE)):
            render(schema, model_type=model_type)


@pytest.mark.parametrize("payload", ["EmailStr", "PositiveInt", "conint(gt=10, lt=20)", "condecimal(max_digits=10)"])
def test_pydantic_class_still_accepts_the_documented_forms(payload: str) -> None:
    schema = {
        "type": "record",
        "name": "User",
        "fields": [{"name": "email", "type": {"type": "string", "pydantic-class": payload}}],
    }

    assert f"pydantic.{payload}" in render(schema, model_type=ModelType.PYDANTIC.value)


def test_ordinary_schemas_are_still_accepted() -> None:
    """Dotted namespaces and free text aliases are valid and must keep working."""
    schema = {
        "type": "record",
        "name": "User",
        "namespace": "some.name.space",
        "aliases": ["My favorite User", "test-schema"],
        "fields": [
            {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16, "namespace": "md5"}},
            {
                "name": "status",
                "type": {"type": "enum", "name": "Status", "symbols": ["ACTIVE", "INACTIVE"]},
                "default": "ACTIVE",
            },
        ],
    }

    source = render(schema)

    assert "some.name.space" in source
    assert "Status.ACTIVE" in source
