import datetime
import enum
import typing
import uuid

import pydantic
import pytest
from pydantic.v1 import Field

from dataclasses_avroschema.pydantic import AvroBaseModel, v1


@pytest.fixture
def AvroBaseModelV1():
    class Bus(v1.AvroBaseModel):
        "A Bus"

        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    class Car(v1.AvroBaseModel):
        "A Car"

        engine_name: str

        class Meta:
            namespace = "types.car_type"

    class TripDistance(str, enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"

    class UnionSchema(v1.AvroBaseModel):
        "Some Unions"

        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.UUID]
        lake_trip: typing.Union[Bus, Car] = Field(default_factory=lambda: Bus(engine_name="honda"))
        river_trip: typing.Optional[typing.Union[Bus, Car]] = None
        mountain_trip: typing.Union[Bus, Car] = Field(default_factory=lambda: Bus.parse_obj({"engine_name": "honda"}))
        trip_distance: typing.Union[int, TripDistance] = 123

    return UnionSchema


@pytest.fixture
def AvroBaseModelV2():
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
        lake_trip: typing.Union[Bus, Car] = pydantic.Field(default_factory=lambda: Bus(engine_name="honda"))
        river_trip: typing.Optional[typing.Union[Bus, Car]] = None
        mountain_trip: typing.Union[Bus, Car] = pydantic.Field(
            default_factory=lambda: Bus.parse_obj({"engine_name": "honda"})
        )
        trip_distance: typing.Union[int, TripDistance] = 123

    return UnionSchema
