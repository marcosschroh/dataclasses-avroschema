import dataclasses
import datetime
import json
import typing
import uuid

from dataclasses_avroschema import AvroModel


def test_schema_with_complex_types(user_advance_dataclass, user_advance_avro_json):
    assert user_advance_dataclass.avro_schema() == json.dumps(user_advance_avro_json)


def test_schema_with_complex_types_and_defaults(
    user_advance_with_defaults_dataclass, user_advance_with_defaults_avro_json
):
    assert user_advance_with_defaults_dataclass.avro_schema() == json.dumps(user_advance_with_defaults_avro_json)


def test_schema_with_unions_type(union_type_schema):
    class Bus(AvroModel):
        "A Bus"
        engine_name: str

    class Car(AvroModel):
        "A Car"
        engine_name: str

    class UnionSchema(AvroModel):
        "Some Unions"
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Union[Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: {"engine_name": "honda"})

    assert UnionSchema.avro_schema() == json.dumps(union_type_schema)
