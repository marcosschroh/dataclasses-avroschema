import dataclasses
import datetime
import json
import typing
import uuid

from dataclasses_avroschema import SchemaGenerator


def test_schema_with_complex_types(user_advance_dataclass, user_advance_avro_json):
    user_schema = SchemaGenerator(user_advance_dataclass, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_advance_avro_json)


def test_schema_with_complex_types_and_defaults(
    user_advance_with_defaults_dataclass, user_advance_with_defaults_avro_json
):
    user_schema = SchemaGenerator(user_advance_with_defaults_dataclass, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_advance_with_defaults_avro_json)


def test_schema_with_unions_type(union_type_schema):
    class Bus:
        "A Bus"
        engine_name: str

    class Car:
        "A Car"
        engine_name: str

    class UnionSchema:
        "Some Unions"
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Union[Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: {"engine_name": "honda"})

    schema = SchemaGenerator(UnionSchema).avro_schema()
    assert schema == json.dumps(union_type_schema)
