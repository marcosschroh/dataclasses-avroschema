import datetime
import json
import uuid
import decimal

from dataclasses_avroschema import AvroModel, types
from dataclasses import field



def test_logical_types_schema(logical_types_schema):
    """
    Test a schema with Logical Types
    """
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)

    class LogicalTypes(AvroModel):
        "Some logical types"
        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"

    assert LogicalTypes.avro_schema() == json.dumps(logical_types_schema)


# def test_decimal_types_schema(decimal_types_schema):
#     """
#     Test a schema with decimal types
#     """
#
#     class DecimalTest(AvroModel):
#         "Some Decimal Tests"
#         # Implicit scale and precision
#         decimal_nodefault: decimal.Decimal  # Error out? Pull precision from context and default scale?
#         decimal_decimal_default: decimal.Decimal = decimal.Decimal('3.14')  # Precision from context, scale from .as_tuple
#
#         # Explicit scale and precision
#         # decimal_default_typed: decimal.Decimal = field(scale=2, precision=3)
#
#     print(DecimalTest.avro_schema())
#
#     assert DecimalTest.avro_schema() == json.dumps(decimal_types_schema)
