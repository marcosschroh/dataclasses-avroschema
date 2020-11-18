import datetime
import decimal
import uuid
from dataclasses import dataclass

import pytz

from dataclasses_avroschema import AvroModel, serialization, types

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)
a_datetime = pytz.utc.localize(a_datetime)


def test_logical_types():
    @dataclass
    class LogicalTypes(AvroModel):
        "Some logical types"
        birthday: datetime.date
        meeting_time: datetime.time
        release_datetime: datetime.datetime
        event_uuid: uuid.uuid4

    data = {
        "birthday": a_datetime.date(),
        "meeting_time": a_datetime.time(),
        "release_datetime": a_datetime,
        "event_uuid": uuid.UUID("09f00184-7721-4266-a955-21048a5cc235"),
    }

    data_json = {
        "birthday": serialization.date_to_str(a_datetime.date()),
        "meeting_time": serialization.time_to_str(a_datetime.time()),
        "release_datetime": serialization.datetime_to_str(a_datetime),
        "event_uuid": "09f00184-7721-4266-a955-21048a5cc235",
    }

    logical_types = LogicalTypes(**data)

    avro_binary = logical_types.serialize()
    avro_json = logical_types.serialize(serialization_type="avro-json")

    assert logical_types.deserialize(avro_binary, create_instance=False) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert logical_types.deserialize(avro_binary) == logical_types
    assert logical_types.deserialize(avro_json, serialization_type="avro-json") == logical_types

    assert logical_types.to_json() == data_json


def test_logical_types_with_defaults():
    @dataclass
    class LogicalTypes(AvroModel):
        "Some logical types"
        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"
        implicit_decimal: decimal.Decimal = decimal.Decimal("3.14")
        explicit_decimal: decimal.Decimal = types.Decimal(scale=5, precision=7)
        explicit_decimal_with_default: decimal.Decimal = types.Decimal(
            scale=5, precision=6, default=decimal.Decimal("3.14159")
        )

    data = {
        "birthday": a_datetime.date(),
        "meeting_time": a_datetime.time(),
        "release_datetime": a_datetime,
        "event_uuid": uuid.UUID("09f00184-7721-4266-a955-21048a5cc235"),
        "implicit_decimal": decimal.Decimal("2.72"),
        "explicit_decimal": decimal.Decimal("1.00"),
        "explicit_decimal_with_default": decimal.Decimal("3.14159"),
    }

    data_json = {
        "birthday": serialization.date_to_str(a_datetime.date()),
        "meeting_time": serialization.time_to_str(a_datetime.time()),
        "release_datetime": serialization.datetime_to_str(a_datetime),
        "event_uuid": "09f00184-7721-4266-a955-21048a5cc235",
        "implicit_decimal": "2.72",
        "explicit_decimal": "1.00",
        "explicit_decimal_with_default": "3.14159",
    }

    logical_types = LogicalTypes(**data)

    avro_binary = logical_types.serialize()
    avro_json = logical_types.serialize(serialization_type="avro-json")

    assert logical_types.deserialize(avro_binary, create_instance=False) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert logical_types.deserialize(avro_binary) == logical_types
    assert logical_types.deserialize(avro_json, serialization_type="avro-json") == logical_types

    assert logical_types.to_json() == data_json


# A decimal.Decimal default is serialized into bytes by dataclasses-avroschema to be deserialized by fastavro
# this test is to make sure that process works as expected
def test_decimals_defaults():
    @dataclass
    class LogicalTypes(AvroModel):
        "Some logical types"
        implicit_decimal: decimal.Decimal = decimal.Decimal("3.14")
        explicit_decimal_with_default: decimal.Decimal = types.Decimal(
            scale=5, precision=6, default=decimal.Decimal("3.14159")
        )
        negative_default: decimal.Decimal = types.Decimal(scale=2, precision=3, default=decimal.Decimal("-1.23"))

    data = {
        "implicit_decimal": decimal.Decimal("3.14"),
        "explicit_decimal_with_default": decimal.Decimal("3.14159"),
        "negative_default": decimal.Decimal("-1.23"),
    }

    data_json = {"implicit_decimal": "3.14", "explicit_decimal_with_default": "3.14159", "negative_default": "-1.23"}

    logical_types = LogicalTypes()

    # Serialize out to capture the defaults
    avro_binary = logical_types.serialize()
    avro_json = logical_types.serialize(serialization_type="avro-json")

    # Deserialize and compare to expected defaults
    assert logical_types.deserialize(avro_binary, create_instance=False) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert logical_types.to_json() == data_json
