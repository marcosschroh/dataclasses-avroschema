import datetime
import decimal
import uuid

import pytest

from dataclasses_avroschema import field_utils, fields, types

from . import consts


@pytest.mark.parametrize("python_type,avro_type,logical_type", consts.LOGICAL_TYPES_AND_DEFAULTS)
def test_logical_types(python_type, avro_type, logical_type):
    name = "a logical type"
    python_type = python_type
    field = fields.AvroField(name, python_type)

    expected = {"name": name, "type": {"type": avro_type, "logicalType": logical_type}}

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_type,avro_type,logical_type", consts.LOGICAL_TYPES_AND_DEFAULTS)
def test_logical_types_with_null_as_default(python_type, avro_type, logical_type):
    name = "a logical type"
    python_type = python_type
    field = fields.AvroField(name, python_type, default=None)

    expected = {
        "name": name,
        "type": ["null", {"type": avro_type, "logicalType": logical_type}],
        "default": None,
    }

    assert expected == field.to_dict()


def test_logical_type_date_with_default():
    name = "a date"
    python_type = datetime.date
    field = fields.AvroField(name, python_type, default=consts.now.date())

    date_time = datetime.datetime.combine(consts.now, datetime.datetime.min.time())
    ts = (date_time - datetime.datetime(1970, 1, 1)).total_seconds()

    expected = {
        "name": name,
        "type": {"type": field_utils.INT, "logicalType": field_utils.DATE},
        "default": ts / (3600 * 24),
    }

    assert expected == field.to_dict()


def test_logical_type_time_millis_with_default() -> None:
    name = "a time"
    python_type = datetime.time
    time = consts.now.time()
    field = fields.AvroField(name, python_type, default=time)

    hour, minutes, seconds, microseconds = (
        time.hour,
        time.minute,
        time.second,
        time.microsecond,
    )
    miliseconds = int((((hour * 60 + minutes) * 60 + seconds) * 1000) + (microseconds / 1000))
    expected = {
        "name": name,
        "type": {"type": field_utils.INT, "logicalType": field_utils.TIME_MILLIS},
        "default": miliseconds,
    }

    assert expected == field.to_dict()


def test_logical_type_time_micros_with_default() -> None:
    name = "a time"
    python_type = types.TimeMicro
    time = consts.now.time()
    field = fields.AvroField(name, python_type, default=time)

    hour, minutes, seconds, microseconds = (
        time.hour,
        time.minute,
        time.second,
        time.microsecond,
    )
    microseconds = float(((hour * 60 + minutes) * 60 + seconds) * 1000000) + microseconds

    expected = {
        "name": name,
        "type": {"type": field_utils.LONG, "logicalType": field_utils.TIME_MICROS},
        "default": microseconds,
    }

    print(field, "marcos;")
    assert expected == field.to_dict()


def test_logical_type_datetime_micros_with_default() -> None:
    name = "a datetime"
    python_type = types.DateTimeMicro
    field = fields.AvroField(name, python_type, default=consts.now)

    ts = consts.now.timestamp()

    expected = {
        "name": name,
        "type": {"type": field_utils.LONG, "logicalType": field_utils.TIMESTAMP_MICROS},
        "default": ts * 1000000,
    }

    assert expected == field.to_dict()


def test_logical_type_datetime_with_default() -> None:
    name = "a datetime"
    python_type = datetime.datetime
    field = fields.AvroField(name, python_type, default=consts.now)

    ts = consts.now.timestamp()

    expected = {
        "name": name,
        "type": {"type": field_utils.LONG, "logicalType": field_utils.TIMESTAMP_MILLIS},
        "default": int(ts * 1000),
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize(
    "python_type",
    (
        uuid.uuid4,
        uuid.UUID,
    ),
)
def test_logical_type_uuid_with_default(python_type) -> None:
    name = "a uuid"
    default = uuid.UUID("d793fc4f-2eef-440a-af8b-a8e884d7b1a8")
    field = fields.AvroField(name, python_type, default=default)

    expected = {
        "name": name,
        "type": {"type": field_utils.STRING, "logicalType": field_utils.UUID},
        "default": str(default),
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("logical_type,invalid_default,msg", consts.LOGICAL_TYPES_AND_INVALID_DEFAULTS)
def test_invalid_default_values(logical_type, invalid_default, msg):
    name = "a_field"
    field = fields.AvroField(name, logical_type, default=invalid_default)

    msg = msg or f"Invalid default type. Default should be {logical_type}"
    with pytest.raises(AssertionError, match=msg):
        field.to_dict()


def test_decimal_type():
    """
    When the type is types.Decimal, the Avro field type should be bytes,
    with logicalType=decimal and metadata attributes scale, precision present as ints
    """
    name = "a_decimal_field"
    # A default decimal.Decimal sets precision and scale implicitly
    default = decimal.Decimal("3.14")
    python_type = types.condecimal(max_digits=3, decimal_places=2)
    field = fields.AvroField(name, python_type, default=default)

    expected = {
        "name": name,
        "type": {
            "type": "bytes",
            "logicalType": "decimal",
            "precision": 3,
            "scale": 2,
        },
        "default": "\\u013a",
    }

    assert expected == field.to_dict()

    # Use types.Decimal to set explicitly
    python_type = types.condecimal(max_digits=7, decimal_places=5)
    field = fields.AvroField(name, python_type)

    expected = {
        "name": name,
        "type": {
            "type": "bytes",
            "logicalType": "decimal",
            "precision": 7,
            "scale": 5,
        },
    }

    assert expected == field.to_dict()

    python_type = types.condecimal(max_digits=7, decimal_places=5)
    field = fields.AvroField(name, python_type, default=decimal.Decimal("3.14"))

    expected = {
        "name": name,
        "type": {
            "type": "bytes",
            "logicalType": "decimal",
            "precision": 7,
            "scale": 5,
        },
        "default": "\\u04ca90",
    }

    assert expected == field.to_dict()

    python_type = types.condecimal(max_digits=7, decimal_places=5)
    field = fields.AvroField(name, python_type, default=None)

    expected = {
        "name": name,
        "type": ["null", {"type": "bytes", "logicalType": "decimal", "precision": 7, "scale": 5}],
        "default": None,
    }

    assert expected == field.to_dict()

    # Validate 0 <= scale <= precision
    with pytest.raises(
        ValueError, match="`decimal_places` must be zero or a positive integer less than or equal to the precision."
    ):
        python_type = types.condecimal(max_digits=1, decimal_places=-1)
        field = fields.AvroField(name, python_type)

        field.to_dict()

    # Validate 0 <= scale <= precision
    with pytest.raises(
        ValueError, match="`decimal_places` must be zero or a positive integer less than or equal to the precision."
    ):
        python_type = types.condecimal(max_digits=1, decimal_places=3)
        field = fields.AvroField(name, python_type)

        field.to_dict()

    # Validate precision >= 0
    with pytest.raises(ValueError, match="`max_digits` must be a positive integer greater than zero"):
        python_type = types.condecimal(max_digits=-1, decimal_places=2)
        field = fields.AvroField(name, python_type)

        field.to_dict()

    # Catch unexpected default value for decimal.Decimal
    with pytest.raises(ValueError):
        default = 7
        field = fields.AvroField(name, python_type, default=default)

        field.to_dict()

    # Default decimal.Decimal has more digits than listed precision
    with pytest.raises(ValueError):
        python_type = types.condecimal(max_digits=3, decimal_places=2)
        field = fields.AvroField(name, python_type, default=decimal.Decimal("3.14159"))

        field.to_dict()

    # Default decimal.Decimal has more digits past decimal than scale
    with pytest.raises(ValueError):
        python_type = types.condecimal(max_digits=3, decimal_places=1)
        field = fields.AvroField(name, python_type, default=decimal.Decimal("3.14"))

        field.to_dict()

    # Just for code coverage
    with pytest.raises(ValueError):
        python_type = types.condecimal(max_digits=3, decimal_places=1)
        field = fields.AvroField(name, python_type, default=decimal.Decimal("3.14"))

        field.to_dict()
