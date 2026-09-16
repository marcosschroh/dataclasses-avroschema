"""Tests for cross-file schema reference support in ModelGenerator."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from dataclasses_avroschema import ModelGenerator

GENERATOR_LOGGER = "dataclasses_avroschema.model_generator.generator"


# Fixtures


@pytest.fixture()
def schemas_dir(tmp_path: Path) -> Path:
    """
    A temp directory with three cross-file schemas forming a chain:

      01-address.avsc  -> defines com.example.Address
      02-person.avsc   -> references com.example.Address
      03-company.avsc  -> references com.example.Person
    """
    address = {
        "type": "record",
        "name": "Address",
        "namespace": "com.example",
        "fields": [
            {"name": "street", "type": "string"},
            {"name": "city", "type": "string"},
        ],
    }
    person = {
        "type": "record",
        "name": "Person",
        "namespace": "com.example",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "address", "type": "com.example.Address"},
        ],
    }
    company = {
        "type": "record",
        "name": "Company",
        "namespace": "com.example",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "ceo", "type": "com.example.Person"},
        ],
    }
    (tmp_path / "01-address.avsc").write_text(json.dumps(address))
    (tmp_path / "02-person.avsc").write_text(json.dumps(person))
    (tmp_path / "03-company.avsc").write_text(json.dumps(company))
    return tmp_path


@pytest.fixture()
def address_schema() -> dict:
    return {
        "type": "record",
        "name": "Address",
        "namespace": "com.example",
        "fields": [
            {"name": "street", "type": "string"},
            {"name": "city", "type": "string"},
        ],
    }


@pytest.fixture()
def person_schema() -> dict:
    return {
        "type": "record",
        "name": "Person",
        "namespace": "com.example",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "address", "type": "com.example.Address"},
        ],
    }


@pytest.fixture()
def conflicting_address_schema() -> dict:
    """Same fullname as `address_schema`, different fields."""
    return {
        "type": "record",
        "name": "Address",
        "namespace": "com.example",
        "fields": [{"name": "zipcode", "type": "string"}],
    }


# validate_schema


def test_validate_schema_raises_unknown_type_without_named_schemas(person_schema):
    """
    Baseline: validate_schema([person]) raises UnknownType when Address is not
    in the schemas list and no named_schemas dict is supplied.
    """
    import fastavro

    with pytest.raises(fastavro.schema.UnknownType):
        ModelGenerator.validate_schema(schemas=[person_schema])


def test_validate_schema_resolves_cross_file_reference_with_named_schemas(address_schema, person_schema):
    """
    validate_schema([person], named_schemas=ns) succeeds after address has been
    validated into the same *ns* dict.
    """
    ns: dict = {}
    # First call registers Address into ns
    ModelGenerator.validate_schema(schemas=[address_schema], named_schemas=ns)
    assert "com.example.Address" in ns

    # Second call resolves com.example.Address from ns -- no UnknownType
    ModelGenerator.validate_schema(schemas=[person_schema], named_schemas=ns)
    assert "com.example.Person" in ns


# render_module with named_schemas


def test_render_module_cross_file_with_named_schemas(address_schema, person_schema):
    """
    render_module([person], named_schemas=ns) renders Person without raising
    UnknownType after address has been rendered into the same ns dict.
    """
    mg = ModelGenerator()
    ns: dict = {}

    mg.render_module(schemas=[address_schema], model_type="dataclass", named_schemas=ns)

    # Should not raise
    code = mg.render_module(schemas=[person_schema], model_type="dataclass", named_schemas=ns)
    assert "class Person" in code
    # the reference must render as the referenced model, not as a fallback type
    assert "address: Address" in code
    assert "name: str" in code


def test_render_module_three_level_chain(schemas_dir: Path):
    """
    Company -> Person -> Address chain resolved via a shared named_schemas dict.
    """
    mg = ModelGenerator()
    ns: dict = {}

    rendered = {}
    for avsc in sorted(schemas_dir.glob("*.avsc")):
        schema = json.loads(avsc.read_text())
        rendered[avsc.stem] = mg.render_module(schemas=[schema], model_type="dataclass", named_schemas=ns)

    assert "class Address" in rendered["01-address"]
    assert "class Person" in rendered["02-person"]
    assert "address: Address" in rendered["02-person"]
    assert "class Company" in rendered["03-company"]
    assert "ceo: Person" in rendered["03-company"]


def test_render_files_generated_models_are_correctly_typed_at_runtime(schemas_dir: Path):
    """
    The generated code does not just compile: executing it yields models whose
    cross-file fields are the referenced classes.
    """
    code = ModelGenerator.render_files(
        sorted(schemas_dir.glob("*.avsc")),
        model_type="dataclass",
    )
    namespace: dict = {}
    exec(compile(code, "<generated>", "exec"), namespace)  # noqa: S102

    address_cls = namespace["Address"]
    person_cls = namespace["Person"]
    company_cls = namespace["Company"]

    company = company_cls(
        name="acme",
        ceo=person_cls(name="jane", address=address_cls(street="main st", city="springfield")),
    )
    assert isinstance(company.ceo, person_cls)
    assert isinstance(company.ceo.address, address_cls)
    assert company.ceo.address.city == "springfield"


def test_render_module_named_schemas_is_backward_compatible(address_schema):
    """
    Existing callers that do not pass named_schemas still work correctly.
    """
    mg = ModelGenerator()
    code = mg.render_module(schemas=[address_schema], model_type="dataclass")
    assert "class Address" in code


# render_files


def test_render_files_resolves_cross_file_references(schemas_dir: Path):
    """
    render_files() renders all schemas from multiple .avsc files in one call,
    automatically resolving cross-file named-type references.
    """
    code = ModelGenerator.render_files(
        sorted(schemas_dir.glob("*.avsc")),
        model_type="dataclass",
    )
    assert "class Address" in code
    assert "class Person" in code
    assert "class Company" in code
    # Each cross-file reference must resolve to the referenced model type.
    assert "address: Address" in code
    assert "ceo: Person" in code


def test_render_files_produces_valid_python(schemas_dir: Path):
    """
    The rendered code is syntactically valid Python that can be compiled.
    """
    code = ModelGenerator.render_files(
        sorted(schemas_dir.glob("*.avsc")),
        model_type="dataclass",
    )
    # compile() raises SyntaxError if the code is invalid
    compile(code, "<generated>", "exec")


def test_render_files_single_file(schemas_dir: Path):
    """render_files() works with a single self-contained .avsc file."""
    code = ModelGenerator.render_files(
        [schemas_dir / "01-address.avsc"],
        model_type="dataclass",
    )
    assert "class Address" in code


def test_render_files_accepts_string_paths(schemas_dir: Path):
    """paths can be plain strings, not only pathlib.Path objects."""
    paths = [str(p) for p in sorted(schemas_dir.glob("*.avsc"))]
    code = ModelGenerator.render_files(paths, model_type="dataclass")
    assert "class Address" in code


def test_render_files_forwards_include_original_schema(schemas_dir: Path):
    """
    include_original_schema must reach the underlying model generator.

    Regression guard: render_files accepted the flag and passed it to the
    constructor, but then called render_module() without it.  render_module
    unconditionally assigns its own default (False) onto the generator, so
    the caller's True was silently discarded.
    """
    without = ModelGenerator.render_files(
        [schemas_dir / "01-address.avsc"],
        model_type="dataclass",
    )
    with_schema = ModelGenerator.render_files(
        [schemas_dir / "01-address.avsc"],
        model_type="dataclass",
        include_original_schema=True,
    )

    assert "original_schema" not in without
    assert "original_schema" in with_schema


# enum cross-file reference


def test_enum_cross_file_reference_with_named_schemas(tmp_path: Path):
    """Enum types defined in a separate file are also resolved correctly."""
    priority_enum = {
        "type": "enum",
        "name": "Priority",
        "namespace": "com.example",
        "symbols": ["LOW", "MEDIUM", "HIGH"],
    }
    task = {
        "type": "record",
        "name": "Task",
        "namespace": "com.example",
        "fields": [
            {"name": "title", "type": "string"},
            {"name": "priority", "type": "com.example.Priority"},
        ],
    }
    (tmp_path / "01-priority.avsc").write_text(json.dumps(priority_enum))
    (tmp_path / "02-task.avsc").write_text(json.dumps(task))

    code = ModelGenerator.render_files(
        sorted(tmp_path.glob("*.avsc")),
        model_type="dataclass",
    )
    assert "class Priority" in code
    assert "class Task" in code
    assert "priority: Priority" in code


# input shapes


def test_validate_schema_accepts_a_bare_schema_dict(address_schema):
    """
    A single schema dict is accepted and treated as a one-element list.

    Regression guard: iterating a dict yields its keys, so the per-schema loop
    would parse the string "type" and raise a misleading
    ``UnknownType: type``.
    """
    ns: dict = {}
    ModelGenerator.validate_schema(schemas=address_schema, named_schemas=ns)
    assert "com.example.Address" in ns


# conflicting redefinitions


def test_validate_schema_warns_on_conflicting_redefinition(address_schema, conflicting_address_schema, caplog):
    """Redefining a name with a different definition warns, and the last one wins."""
    ns: dict = {}
    ModelGenerator.validate_schema(schemas=[address_schema], named_schemas=ns)

    with caplog.at_level(logging.WARNING, logger=GENERATOR_LOGGER):
        ModelGenerator.validate_schema(schemas=[conflicting_address_schema], named_schemas=ns)

    assert "com.example.Address" in caplog.text
    # the overwrite is not prevented, only reported
    assert [f["name"] for f in ns["com.example.Address"]["fields"]] == ["zipcode"]


def test_validate_schema_warns_on_conflicting_redefinition_within_one_call(
    address_schema, conflicting_address_schema, caplog
):
    """A conflict between two schemas passed in the same call also warns."""
    with caplog.at_level(logging.WARNING, logger=GENERATOR_LOGGER):
        ModelGenerator.validate_schema(schemas=[address_schema, conflicting_address_schema])

    assert "com.example.Address" in caplog.text


def test_validate_schema_is_quiet_on_identical_redefinition(address_schema, caplog):
    """Re-registering the identical definition is not a conflict and stays quiet."""
    ns: dict = {}
    ModelGenerator.validate_schema(schemas=[address_schema], named_schemas=ns)

    with caplog.at_level(logging.WARNING, logger=GENERATOR_LOGGER):
        ModelGenerator.validate_schema(schemas=[dict(address_schema)], named_schemas=ns)

    assert caplog.text == ""
    assert [f["name"] for f in ns["com.example.Address"]["fields"]] == ["street", "city"]


def test_metadata_only_redefinition_still_warns(address_schema, caplog):
    """
    A redefinition differing only in metadata warns as well.

    `aliases` lands in `Meta` and `doc` becomes the class docstring, so the two
    definitions do produce different models.
    """
    mg = ModelGenerator()
    plain = mg.render_module(schemas=[address_schema], model_type="dataclass")
    aliased = mg.render_module(schemas=[{**address_schema, "aliases": ["OldAddress"]}], model_type="dataclass")
    documented = mg.render_module(schemas=[{**address_schema, "doc": "a postal address"}], model_type="dataclass")

    assert "aliases" not in plain
    assert "aliases = ['OldAddress']" in aliased
    assert "a postal address" in documented

    ns: dict = {}
    ModelGenerator.validate_schema(schemas=[address_schema], named_schemas=ns)

    with caplog.at_level(logging.WARNING, logger=GENERATOR_LOGGER):
        ModelGenerator.validate_schema(schemas=[{**address_schema, "aliases": ["OldAddress"]}], named_schemas=ns)

    assert "com.example.Address" in caplog.text
