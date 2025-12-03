import dataclasses
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
    delta = datetime.timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5, milliseconds=6, microseconds=7)

    class LogicalTypes(AvroModel):
        "Some logical types"

        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        time_elapsed: datetime.timedelta = delta
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


def test_uuid_with_forward_ref_not_treated_as_self_reference():
    """
    Test that ForwardRef('UUID') inside a Union is NOT incorrectly treated as a
    self-reference. This simulates the case where UUID is imported under TYPE_CHECKING.

    See: https://github.com/marcosschroh/dataclasses-avroschema/issues/912
    """

    # Simulate TYPE_CHECKING import: Optional["UUID"] becomes Union[ForwardRef('UUID'), None]
    @dataclasses.dataclass
    class FooWithForwardRefUUID(AvroModel):
        # This annotation mimics what happens when UUID is under TYPE_CHECKING
        # The annotation becomes ForwardRef('UUID') | None at runtime
        _uuid: Optional["uuid.UUID"] = None

    schema = json.loads(FooWithForwardRefUUID.avro_schema())

    # The UUID field should be a proper logical type, NOT a string "uuid.UUID"
    uuid_field = schema["fields"][0]
    assert uuid_field["name"] == "_uuid"

    # Expected: ["null", {"type": "string", "logicalType": "uuid"}]
    # Bug (before fix): ["null", "uuid.UUID"]
    assert uuid_field["type"] == ["null", {"type": "string", "logicalType": "uuid"}], (
        f"UUID field should use logical type, not string. Got: {uuid_field['type']}"
    )


def test_self_reference_still_works_with_forward_ref_fix():
    """
    Test that actual self-references still work correctly after the ForwardRef fix.
    This ensures we didn't break self-referential types while fixing issue #912.

    Scenario: Foo has both a self-reference field AND a ForwardRef UUID field.
    - The self-reference should produce the class name as type
    - The UUID should produce the logical type
    """

    @dataclasses.dataclass
    class Foo(AvroModel):
        name: str
        # Self-reference: ForwardRef('Foo') should be treated as self-reference
        friend: Optional["Foo"] = None
        # UUID ForwardRef: should resolve to UUID logical type, NOT self-reference
        _uuid: Optional["uuid.UUID"] = None

    schema = json.loads(Foo.avro_schema())

    # Find fields by name
    fields = {f["name"]: f for f in schema["fields"]}

    # Verify self-reference field produces class name
    friend_field = fields["friend"]
    assert friend_field["type"] == ["null", "Foo"], (
        f"Self-reference should produce class name. Got: {friend_field['type']}"
    )

    # Verify UUID field produces logical type, not string
    uuid_field = fields["_uuid"]
    assert uuid_field["type"] == ["null", {"type": "string", "logicalType": "uuid"}], (
        f"UUID should be logical type, not string. Got: {uuid_field['type']}"
    )


def test_nested_class_with_forward_ref_uuid():
    """
    Test that nested classes with ForwardRef types work correctly.

    Scenario: Foo contains Bar, and Bar has a ForwardRef UUID field.
    Both the nested relationship and UUID resolution should work.
    """

    @dataclasses.dataclass
    class Bar(AvroModel):
        value: str
        bar_uuid: Optional["uuid.UUID"] = None

    @dataclasses.dataclass
    class Foo(AvroModel):
        name: str
        bar: Optional[Bar] = None
        foo_uuid: Optional["uuid.UUID"] = None

    schema = json.loads(Foo.avro_schema())
    fields = {f["name"]: f for f in schema["fields"]}

    # Verify Foo's UUID field is a logical type
    foo_uuid_field = fields["foo_uuid"]
    assert foo_uuid_field["type"] == ["null", {"type": "string", "logicalType": "uuid"}], (
        f"Foo's UUID should be logical type. Got: {foo_uuid_field['type']}"
    )

    # Verify Bar is properly nested (not treated as self-reference)
    bar_field = fields["bar"]
    assert bar_field["type"][0] == "null"
    bar_record = bar_field["type"][1]
    assert bar_record["type"] == "record"
    assert bar_record["name"] == "Bar"

    # Verify Bar's UUID field inside the nested record
    bar_fields = {f["name"]: f for f in bar_record["fields"]}
    bar_uuid_field = bar_fields["bar_uuid"]
    assert bar_uuid_field["type"] == ["null", {"type": "string", "logicalType": "uuid"}], (
        f"Bar's UUID should be logical type. Got: {bar_uuid_field['type']}"
    )
