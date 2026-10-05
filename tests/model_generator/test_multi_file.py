"""Tests for cross-file schema reference support in ModelGenerator."""

from __future__ import annotations

from unittest import mock

from dataclasses_avroschema import ModelGenerator


def test_validate_schema_forwards_named_schemas_to_fastavro():
    """validate_schema is a thin pass-through: fastavro does the actual work."""
    schema = {
        "type": "record",
        "name": "Person",
        "namespace": "com.example",
        "fields": [{"name": "name", "type": "string"}],
    }
    ns: dict = {}
    with mock.patch("dataclasses_avroschema.model_generator.generator.fastavro.parse_schema") as parse_schema:
        ModelGenerator.validate_schema(schemas=[schema], named_schemas=ns)

    parse_schema.assert_called_once_with([schema], named_schemas=ns)
