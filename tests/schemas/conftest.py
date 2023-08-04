import datetime
import enum
import json
import os
import typing
import uuid

import pytest
from pydantic import Field

from dataclasses_avroschema.avrodantic import AvroBaseModel

AVRO_SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avro")


def load(fp):
    with open(fp, mode="r") as f:
        return f.read()


def load_json(file_name):
    schema_path = os.path.join(AVRO_SCHEMAS_DIR, file_name)
    schema_string = load(schema_path)
    return json.loads(schema_string)


@pytest.fixture
def user_avro_json():
    return load_json("user.avsc")


@pytest.fixture
def user_with_field_metadata_avro_json():
    return load_json("user_with_field_metadata.avsc")


@pytest.fixture
def user_v2_avro_json():
    return load_json("user_v2.avsc")


@pytest.fixture
def user_advance_avro_json():
    return load_json("user_advance.avsc")


@pytest.fixture
def user_advance_with_defaults_avro_json():
    return load_json("user_advance_with_defaults.avsc")


@pytest.fixture
def user_extra_avro_attributes():
    return load_json("user_extra_avro_attributes.avsc")


@pytest.fixture
def user_one_address_schema():
    return load_json("user_one_address.avsc")


@pytest.fixture
def user_one_address_alias_item():
    return load_json("user_one_address_alias_item.avsc")


@pytest.fixture
def user_array_address_alias():
    return load_json("user_array_address_alias.avsc")


@pytest.fixture
def user_map_address_alias():
    return load_json("user_map_address_alias.avsc")


@pytest.fixture
def user_one_address_schema_with_none_default():
    return load_json("user_one_address_with_none_default.avsc")


@pytest.fixture
def user_many_address_schema():
    return load_json("user_many_address.avsc")


@pytest.fixture
def user_many_address_map_schema():
    return load_json("user_many_address_map.avsc")


@pytest.fixture
def user_many_address_map_schema_alias_item():
    return load_json("user_many_address_map_alias_item.avsc")


@pytest.fixture
def user_self_reference_one_to_one_schema():
    return load_json("user_self_reference_one_to_one.avsc")


@pytest.fixture
def user_self_reference_one_to_many_schema():
    return load_json("user_self_reference_one_to_many.avsc")


@pytest.fixture
def user_self_reference_one_to_many_map_schema():
    return load_json("user_self_reference_one_to_many_map.avsc")


@pytest.fixture
def logical_types_schema():
    return load_json("logical_types.avsc")


@pytest.fixture
def logical_types_micro_schemas():
    return load_json("logical_types_micro.avsc")


@pytest.fixture
def union_type_schema():
    return load_json("union_type.avsc")


@pytest.fixture
def default_union_schema():
    return load_json("union_default_type.avsc")

@pytest.fixture
def optional_enum_with_default_schema():
    return load_json("optional_enum_with_default.avsc")

@pytest.fixture
def typing_optional_schema():
    return load_json("union_typing_optional.avsc")


@pytest.fixture
def decimal_types_schema():
    return load_json("decimal.avsc")


@pytest.fixture
def pydantic_fields_schema():
    return load_json("pydantic_fields.avsc")


@pytest.fixture
def order_fields_schema():
    return load_json("order_fields.avsc")


@pytest.fixture
def AvroBaseModel_model():
    class Bus(AvroBaseModel):
        "A Bus"
        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    class Car(AvroBaseModel):
        "A Car"
        engine_name: str

        class Meta:
            namespace = "types.car_type"

    class TripDistance(str, enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"

    class UnionSchema(AvroBaseModel):
        "Some Unions"
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.UUID]
        lake_trip: typing.Union[Bus, Car] = Field(default_factory=lambda: Bus(engine_name="honda"))
        river_trip: typing.Union[Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = Field(default_factory=lambda: {"engine_name": "honda"})
        trip_distance: typing.Union[int, TripDistance] = None

    return UnionSchema
