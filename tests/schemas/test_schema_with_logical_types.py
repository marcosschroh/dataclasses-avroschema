import datetime
import decimal
import json
import uuid

from dataclasses_avroschema import AvroModel, types


def test_logical_types_schema(logical_types_schema):
    """
    Test a schema with Logical Types
    """
    a_datetime = datetime.datetime.fromtimestamp(1570903062, datetime.timezone.utc)

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
    a_datetime = datetime.datetime.fromtimestamp(1570903062, datetime.timezone.utc)

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
        implicit: decimal.Decimal = decimal.Decimal("3.14")
        explicit: decimal.Decimal = types.Decimal(scale=11, precision=13)
        explicit_with_default: decimal.Decimal = types.Decimal(scale=5, precision=7, default=decimal.Decimal("3.14159"))
        explicit_with_null_default: decimal.Decimal = types.Decimal(scale=5, precision=7, default=None)

    assert DecimalTest.avro_schema() == json.dumps(decimal_types_schema)
