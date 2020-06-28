import datetime
import uuid
from dataclasses import dataclass

import pytz

from dataclasses_avroschema import AvroModel, serialization

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

    assert logical_types.deserialize(avro_binary) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json") == data

    assert logical_types.to_json() == data_json


def test_logical_types_with_defaults():
    @dataclass
    class LogicalTypes(AvroModel):
        "Some logical types"
        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"

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

    assert logical_types.deserialize(avro_binary) == data
    assert logical_types.deserialize(avro_json, serialization_type="avro-json") == data

    assert logical_types.to_json() == data_json
