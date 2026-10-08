"""Tests for cross-file schema reference support in ModelGenerator."""

from __future__ import annotations

import json
from pathlib import Path
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


def test_render_files_renders_a_schema_file(tmp_path: Path):
    """render_files() loads a .avsc file from disk and renders it."""
    schema = {
        "type": "record",
        "name": "Address",
        "namespace": "com.example",
        "fields": [{"name": "street", "type": "string"}],
    }
    path = tmp_path / "address.avsc"
    path.write_text(json.dumps(schema))

    code = ModelGenerator.render_files([path], model_type="dataclass")

    assert "class Address" in code
