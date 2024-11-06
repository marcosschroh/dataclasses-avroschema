import datetime
import decimal
import json
import typing
import uuid
from dataclasses import dataclass

import pytest

from dataclasses_avroschema import AvroModel, serialization, types
from dataclasses_avroschema.faust import AvroRecord
from dataclasses_avroschema.pydantic import AvroBaseModel

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)
delta = datetime.timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5, milliseconds=6, microseconds=7)


parametrize_base_model = pytest.mark.parametrize(
    "model_class, decorator", [(AvroModel, dataclass), (AvroBaseModel, lambda f: f), (AvroRecord, lambda f: f)]
)


@parametrize_base_model
def test_logical_types(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    @decorator
    class LogicalTypes(model_class):
        "Some logical types"

        birthday: datetime.date
        meeting_time: datetime.time
        meeting_time_micro: types.TimeMicro
        release_datetime: datetime.datetime
        release_datetime_micro: types.DateTimeMicro
        time_elapsed: datetime.timedelta
        event_uuid: uuid.UUID

    data = {
        "birthday": a_datetime.date(),
        "meeting_time": a_datetime.time(),
        "meeting_time_micro": a_datetime.time(),
        "release_datetime": a_datetime,
        "release_datetime_micro": a_datetime,
        "time_elapsed": delta,
        "event_uuid": uuid.UUID("09f00184-7721-4266-a955-21048a5cc235"),
    }

    data_json = {
        "birthday": serialization.date_to_str(a_datetime.date()),
        "meeting_time": serialization.time_to_str(a_datetime.time()),
        "meeting_time_micro": serialization.time_to_str(a_datetime.time()),
        "release_datetime": serialization.datetime_to_str(a_datetime),
        "release_datetime_micro": serialization.datetime_to_str(a_datetime),
        "time_elapsed": 788645.006007,
        "event_uuid": "09f00184-7721-4266-a955-21048a5cc235",
    }

    logical_types = LogicalTypes(**data)

    avro_binary = logical_types.serialize()
    avro_json = logical_types.serialize(serialization_type="avro-json")

    assert logical_types.deserialize(avro_binary, create_instance=False) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert logical_types.deserialize(avro_binary) == logical_types
    assert logical_types.deserialize(avro_json, serialization_type="avro-json") == logical_types

    assert logical_types.to_json() == json.dumps(data_json)


@parametrize_base_model
def test_logical_union(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    if model_class is AvroRecord:
        pytest.skip(
            reason=(
                "Faust does not support Union of types "
                "(<class 'datetime.datetime'>, <class 'datetime.date'>, <class 'uuid.UUID'>)"
            )
        )

    @decorator
    class UnionSchema(model_class):
        "Some Unions"

        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.UUID]

    data = {
        "logical_union": a_datetime.date(),
    }

    data_json = {
        "logical_union": serialization.date_to_str(a_datetime.date()),
    }

    logical_types = UnionSchema(**data)

    avro_binary = logical_types.serialize()
    avro_json = logical_types.serialize(serialization_type="avro-json")

    assert logical_types.deserialize(avro_binary, create_instance=False) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert logical_types.deserialize(avro_binary) == logical_types
    assert logical_types.deserialize(avro_json, serialization_type="avro-json") == logical_types

    assert logical_types.to_json() == json.dumps(data_json)


@parametrize_base_model
def test_logical_types_with_defaults(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    @decorator
    class LogicalTypes(model_class):
        "Some logical types"

        implicit_decimal: types.condecimal(max_digits=3, decimal_places=2)
        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        meeting_time_micro: types.TimeMicro = a_datetime.time()
        release_datetime_micro: types.DateTimeMicro = a_datetime
        event_uuid: uuid.UUID = uuid.UUID("09f00184-7721-4266-a955-21048a5cc235")
        decimal_with_default: types.condecimal(max_digits=6, decimal_places=5) = decimal.Decimal("3.14159")

    data = {
        "birthday": a_datetime.date(),
        "meeting_time": a_datetime.time(),
        "meeting_time_micro": a_datetime.time(),
        "release_datetime": a_datetime,
        "release_datetime_micro": a_datetime,
        "event_uuid": uuid.UUID("09f00184-7721-4266-a955-21048a5cc235"),
        "implicit_decimal": decimal.Decimal("2.72"),
        "decimal_with_default": decimal.Decimal("3.14159"),
    }

    data_json = {
        "implicit_decimal": "2.72",
        "birthday": serialization.date_to_str(a_datetime.date()),
        "meeting_time": serialization.time_to_str(a_datetime.time()),
        "release_datetime": serialization.datetime_to_str(a_datetime),
        "meeting_time_micro": serialization.time_to_str(a_datetime.time()),
        "release_datetime_micro": serialization.datetime_to_str(a_datetime),
        "event_uuid": "09f00184-7721-4266-a955-21048a5cc235",
        "decimal_with_default": "3.14159",
    }

    logical_types = LogicalTypes(**data)

    avro_binary = logical_types.serialize()
    avro_json = logical_types.serialize(serialization_type="avro-json")

    assert logical_types.deserialize(avro_binary, create_instance=False) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert logical_types.deserialize(avro_binary) == logical_types
    assert logical_types.deserialize(avro_json, serialization_type="avro-json") == logical_types

    assert logical_types.to_json() == json.dumps(data_json)


# A decimal.Decimal default is serialized into bytes by dataclasses-avroschema to be deserialized by fastavro
# this test is to make sure that process works as expected
@parametrize_base_model
def test_decimals_defaults(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    @decorator
    class LogicalTypes(model_class):
        "Some logical types"

        explicit: types.condecimal(max_digits=3, decimal_places=2)
        explicit_decimal_with_default: types.condecimal(max_digits=6, decimal_places=5) = decimal.Decimal("3.14159")
        negative_default: types.condecimal(max_digits=3, decimal_places=2) = decimal.Decimal("-1.23")

    data = {
        "explicit": decimal.Decimal("3.12"),
        "explicit_decimal_with_default": decimal.Decimal("3.14159"),
        "negative_default": decimal.Decimal("-1.23"),
    }

    data_json = {
        "explicit": "3.12",
        "explicit_decimal_with_default": "3.14159",
        "negative_default": "-1.23",
    }
    logical_types = LogicalTypes(explicit=decimal.Decimal("3.12"))

    # Serialize out to capture the defaults
    avro_binary = logical_types.serialize()
    avro_json = logical_types.serialize(serialization_type="avro-json")

    # Deserialize and compare to expected defaults
    assert logical_types.deserialize(avro_binary, create_instance=False) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert logical_types.to_json() == json.dumps(data_json)
