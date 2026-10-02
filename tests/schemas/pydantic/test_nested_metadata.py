"""Regression tests for Pydantic metadata on container type arguments."""
import copy
import datetime
from typing import Annotated, Optional, Union

import pytest
from pydantic import Field, create_model

from dataclasses_avroschema import types
from dataclasses_avroschema.pydantic import AvroBaseModel

MARKER = {"logicalType": "sml.file-ref"}
FileRef = Annotated[str, Field(json_schema_extra={"metadata": MARKER})]
REF_SCHEMA = {"type": "string", **MARKER}


def schema_for(annotation, default=...):
    model = create_model("NestedMetadata", __base__=AvroBaseModel, value=(annotation, default))
    return model.avro_schema_to_python()["fields"][0]


def test_direct_field_keeps_existing_metadata_placement():
    field = schema_for(FileRef)
    assert field == {"name": "value", "type": "string", **MARKER}


@pytest.mark.parametrize("annotation, expected", [
    (list[FileRef], {"type": "array", "items": REF_SCHEMA, "name": "value"}),
    (dict[str, FileRef], {"type": "map", "values": REF_SCHEMA, "name": "value"}),
    (Union[FileRef, int], [REF_SCHEMA, "long"]),
    (Optional[FileRef], [REF_SCHEMA, "null"]),
])
def test_nested_metadata(annotation, expected):
    assert schema_for(annotation)["type"] == expected


def test_optional_null_default():
    field = schema_for(Optional[FileRef], None)
    assert field["type"] == ["null", REF_SCHEMA]
    assert field["default"] is None


@pytest.mark.parametrize("annotation", [Optional[FileRef], Union[int, FileRef]])
def test_non_null_default_does_not_add_duplicate_string_branch(annotation):
    field = schema_for(annotation, "blob://default")
    other = "null" if type(None) in annotation.__args__ else "long"
    assert field["type"] == [REF_SCHEMA, other]
    assert field["default"] == "blob://default"


def test_nested_list_and_union():
    field = schema_for(list[list[Optional[FileRef]]])
    assert field["type"]["items"]["items"] == [REF_SCHEMA, "null"]


def test_outer_metadata_stays_on_outer_field():
    outer = Field(description="References", json_schema_extra={"metadata": {"custom": "outer"}})
    field = schema_for(list[FileRef], outer)
    assert field["doc"] == "References"
    assert field["custom"] == "outer"
    assert field["type"]["items"] == REF_SCHEMA


def test_metadata_dictionaries_are_not_mutated():
    metadata = {"custom": "inner"}
    alias = Annotated[str, Field(json_schema_extra={"metadata": metadata})]
    before = copy.deepcopy(metadata)
    first = schema_for(list[alias])
    assert schema_for(list[alias]) == first
    assert metadata == before


def test_builtin_logical_type_is_preserved():
    alias = Annotated[datetime.date, Field(json_schema_extra={"metadata": {"custom": "date"}})]
    assert schema_for(list[alias])["type"]["items"] == {
        "type": "int", "logicalType": "date", "custom": "date"
    }


def test_library_annotated_type_is_preserved():
    alias = Annotated[types.Int32, Field(json_schema_extra={"metadata": {"custom": "int32"}})]
    assert schema_for(list[alias])["type"]["items"] == {"type": "int", "custom": "int32"}


def test_plain_and_unrecognized_annotations_are_unchanged():
    assert schema_for(list[str])["type"]["items"] == "string"
    assert schema_for(list[Annotated[str, "ignored"]])["type"]["items"] == "string"


def test_annotated_optional_item():
    alias = Annotated[Optional[str], Field(json_schema_extra={"metadata": {"custom": "reference"}})]
    assert schema_for(list[alias])["type"]["items"] == [
        {"type": "string", "custom": "reference"}, "null"
    ]


def test_multiple_metadata_annotations():
    alias = Annotated[str,
        Field(json_schema_extra={"metadata": {"custom": "first", "retained": True}}),
        Field(json_schema_extra={"metadata": {"custom": "last"}}),
    ]
    assert schema_for(list[alias])["type"]["items"] == {
        "type": "string", "custom": "last", "retained": True
    }


def test_serialization_round_trip():
    """Requires real fastavro; run in the normal project environment."""
    class Demo(AvroBaseModel):
        tags: list[FileRef]
        audio: Optional[FileRef] = None

    instance = Demo(tags=["blob://image"], audio="blob://audio")
    restored = Demo.deserialize(instance.serialize())
    assert restored == instance


def test_internal_control_metadata_is_not_emitted():
    alias = Annotated[str, Field(json_schema_extra={"metadata": {
        "custom": "kept", "exclude_default": True, "inner_name": "internal"
    }})]
    assert schema_for(list[alias])["type"]["items"] == {"type": "string", "custom": "kept"}


def test_annotated_array_inside_union():
    alias = Annotated[list[FileRef], Field(json_schema_extra={"metadata": {"custom": "array"}})]
    field = schema_for(Optional[alias], None)
    assert field["type"] == ["null", {
        "type": "array", "items": REF_SCHEMA, "name": "value", "custom": "array"
    }]


def test_plain_fields_without_pydantic_available():
    from dataclasses_avroschema import utils
    from dataclasses_avroschema.fields.fields import AvroField

    original = utils.pydantic
    try:
        utils.pydantic = None
        field = AvroField("value", list[Annotated[str, "ignored"]])
        assert field.get_avro_type()["items"] == "string"
    finally:
        utils.pydantic = original


@pytest.mark.parametrize("nested_first", [False, True])
def test_shared_alias_metadata_does_not_leak_between_models(nested_first):
    metadata = {"logicalType": "sml.file-ref", "aliases": ["original"]}
    alias = Annotated[str, Field(json_schema_extra={"metadata": metadata})]
    before = copy.deepcopy(metadata)
    direct = create_model("Direct", __base__=AvroBaseModel, single=(
        alias, Field(description="top level (already worked)", alias="external")
    ))
    nested = create_model("Nested", __base__=AvroBaseModel,
        many=(list[alias], ...), mapping=(dict[str, alias], ...), optional=(Optional[alias], None))
    if nested_first:
        nested.avro_schema_to_python()
    direct_field = direct.avro_schema_to_python()["fields"][0]
    assert direct_field["doc"] == "top level (already worked)"
    assert set(direct_field["aliases"]) == {"original", "external"}
    fields = nested.avro_schema_to_python()["fields"]
    for schema in (fields[0]["type"]["items"], fields[1]["type"]["values"], fields[2]["type"][1]):
        assert schema["logicalType"] == "sml.file-ref"
        assert "doc" not in schema
        assert schema["aliases"] == ["original"]
    assert metadata == before


def test_recursive_pydantic_map_schema():
    class User(AvroBaseModel):
        name: str
        friends: Optional[dict[str, "User"]] = None
        teamates: Optional[dict[str, "User"]] = None

    schema = User.avro_schema_to_python()
    for field in schema["fields"][1:]:
        assert field["type"][0] == "null"
        assert field["type"][1]["values"] == "User"


def test_recursive_dataclass_map_schema():
    from typing import Type
    from dataclasses_avroschema import AvroModel

    class User(AvroModel):
        name: str
        friends: dict[str, Type["User"]]
        teamates: Optional[dict[str, Type["User"]]] = None

    schema = User.avro_schema_to_python()
    assert schema["fields"][1]["type"]["values"] == "User"
    assert schema["fields"][2]["type"][1]["values"] == "User"
