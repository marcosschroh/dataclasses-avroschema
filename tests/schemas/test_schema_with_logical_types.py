import datetime
import decimal
import json
import uuid
from typing import Optional

from dataclasses_avroschema import AvroModel, types


def test_logical_types_schema(logical_types_schema):
    """
    Test a schema with Logical Types
    """
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)

    class LogicalTypes(AvroModel):
        "Some logical types"

        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"

    assert LogicalTypes.avro_schema() == json.dumps(logical_types_schema)


def test_logical_micro_types_schema(logical_types_micro_schemas):
    """
    Test a schema with Logical Types
    """
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)

    class LogicalTypesMicro(AvroModel):
        "Some logical types"

        time_micros: types.TimeMicro
        datetime_micros: types.DateTimeMicro
        meeting_time: datetime.time = a_datetime.time()
        meeting_datetime: datetime.datetime = a_datetime
        meeting_time_micros: types.TimeMicro = a_datetime.time()
        meeting_datetime_micros: types.DateTimeMicro = a_datetime
        release_datetime: datetime.datetime = a_datetime

    assert LogicalTypesMicro.avro_schema() == json.dumps(logical_types_micro_schemas)


def test_decimal_types_schema(decimal_types_schema):
    """
    Test a schema with decimal types
    """

    class DecimalTest(AvroModel):
        "Some Decimal Tests"

        implicit: types.condecimal(max_digits=3, decimal_places=2)
        explicit: types.condecimal(max_digits=13, decimal_places=11)
        explicit_with_default: types.condecimal(max_digits=7, decimal_places=5) = decimal.Decimal("3.14159")
        explicit_with_null_default: Optional[types.condecimal(max_digits=7, decimal_places=5)] = None

    assert DecimalTest.avro_schema() == json.dumps(decimal_types_schema)
