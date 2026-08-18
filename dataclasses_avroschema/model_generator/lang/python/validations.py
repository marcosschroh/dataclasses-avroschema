"""
Guards for the schema supplied values that the model generator renders into the Python
source it emits.

The schema is not necessarily written by the person running the generator, and whatever
reaches the generated module runs when that module is imported. There are two answers
here, and which one applies is decided by the position the value is rendered into:

* a value that becomes *text* -- the body of a string literal, a docstring -- is escaped,
  so that it cannot terminate the literal it sits in and have the remainder parsed as
  code. That is `escape_string` and `escape_docstring`.
* a value that becomes *code* -- a name in callable position, a namespace inside an
  annotation, an enum member name -- cannot be escaped, because it is meant to be
  evaluated. There is no literal to escape into. Such a value is checked against the
  grammar it is supposed to belong to, and a schema that does not satisfy it is refused.
  That is the `validate_*` functions.
"""

import ast
import json
import re
import typing

from dataclasses_avroschema import exceptions

NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
NAME_RULE = "a name matching [A-Za-z_][A-Za-z0-9_]*"


def validate_name(value: typing.Any, *, location: str) -> str:
    """
    Check that a schema supplied value is an Avro name before it is rendered into an
    identifier position of the generated source.

    Escaping is not available here the way it is for a string literal: the value does
    not become text, it becomes part of an expression that is evaluated when the
    generated module is imported. The Avro specification already requires a name to
    match `[A-Za-z_][A-Za-z0-9_]*`, and this library enforces that rule in the other
    direction, when a schema is produced from a model. A schema that violates it is
    refused rather than rendered.
    """
    name = str(value)

    if not NAME_PATTERN.fullmatch(name):
        raise exceptions.InvalidSchemaValue(value=value, location=location, expected=NAME_RULE)

    return name


def validate_fullname(value: typing.Any, *, location: str) -> str:
    """A namespace is a dot separated sequence of Avro names."""
    fullname = str(value)

    if not all(NAME_PATTERN.fullmatch(part) for part in fullname.split(".")):
        raise exceptions.InvalidSchemaValue(
            value=value, location=location, expected=f"a dot separated sequence of {NAME_RULE}"
        )

    return fullname


def validate_aliases(value: typing.Any) -> typing.List[typing.Any]:
    """
    Aliases are rendered through the `repr` of a list, which quotes every entry, so what
    they contain is already safe and this library uses them as free text. A schema that
    supplies a bare string instead of a list is what reaches the generated source
    unquoted, so only the type is checked.
    """
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise exceptions.InvalidSchemaValue(value=value, location="aliases", expected="a list")

    return list(value)


def _is_literal(node: ast.expr) -> bool:
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        node = node.operand

    return isinstance(node, ast.Constant)


def validate_type_expression(value: typing.Any, *, location: str) -> str:
    """
    Check that a schema supplied type is a name, or a call to a name whose arguments are
    all literals, before it is rendered into an annotation.

    A bare name would be too strict: `pydantic-class` is documented as carrying a
    pydantic type, and a constrained one is written as a call, `conint(gt=10, lt=20)`.
    Anything richer is refused, because the annotation is evaluated when the generated
    module is imported: an operator or an attribute lookup is enough to reach code the
    schema author chose, and a call in an argument position reaches the builtins.
    """
    expression = str(value)
    expected = "a name, or a call to a name with literal arguments"

    try:
        parsed = ast.parse(expression, mode="eval").body
    except SyntaxError:
        raise exceptions.InvalidSchemaValue(value=value, location=location, expected=expected) from None

    if isinstance(parsed, ast.Name):
        return expression

    if isinstance(parsed, ast.Call) and isinstance(parsed.func, ast.Name):
        arguments = [*parsed.args, *(argument.value for argument in parsed.keywords)]

        if all(_is_literal(argument) for argument in arguments):
            return expression

    raise exceptions.InvalidSchemaValue(value=value, location=location, expected=expected)


def escape_string(value: typing.Any) -> str:
    """
    Escape a schema supplied value so it can be placed inside the quotes of a
    generated Python string literal.

    The schema is not necessarily written by the person running the generator, so
    a value that contains a quote, a backslash or a newline must not be able to
    terminate the literal it is rendered into: the remainder would then be parsed
    as code and would run when the generated module is imported.

    `json.dumps` already escapes exactly those characters, and the surrounding
    quotes it adds are dropped because the templates supply their own.
    """
    return json.dumps(str(value), ensure_ascii=False)[1:-1]


def escape_docstring(value: str) -> str:
    """
    Escape a schema supplied value so it can be placed inside a generated docstring.

    The schema is not necessarily written by the person running the generator, and a
    `doc` is copied into the docstring of the class that is emitted. A `\"""` in it
    would close the docstring, leaving the remainder to be parsed as code that runs
    when the generated module is imported; a trailing backslash would escape the
    closing delimiter and have the same effect.

    Escaping every quote covers both, and any run of them. Control characters are
    escaped as well because Python source cannot contain them, only the ones that
    become line breaks in the rendered docstring are kept.
    """
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return "".join(char if char >= " " or char in "\n\r\t" else f"\\x{ord(char):02x}" for char in escaped)
