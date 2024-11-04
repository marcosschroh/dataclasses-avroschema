import datetime
import decimal
import uuid

import pydantic
import pytest

from dataclasses_avroschema import AvroField, types
from dataclasses_avroschema.fields import field_utils

from . import consts


@pytest.mark.parametrize("python_type,avro_type", consts.LOGICAL_TYPES)
def test_logical_types(python_type, avro_type):
    name = "a logical type"
    python_type = python_type
    field = AvroField(name, python_type)

    expected = {"name": name, "type": avro_type}

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_type,avro_type", consts.LOGICAL_TYPES)
def test_logical_types_with_null_as_default(python_type, avro_type):
    name = "a logical type"
    field = AvroField(name, python_type, default=None)

    expected = {
        "name": name,
        "type": ["null", avro_type],
        "default": None,
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_type,avro_type", consts.LOGICAL_TYPES)
def test_logical_types_exclude_default(python_type, avro_type):
    name = "a logical type"
    python_type = python_type
    field = AvroField(name, python_type, default=1, metadata={"exclude_default": True})
    field_with_default_factory = AvroField(
        name, python_type, default_factory=lambda: 1, metadata={"exclude_default": True}
    )

    expected = {"name": name, "type": avro_type}

    assert expected == field.to_dict() == field_with_default_factory.to_dict()


def test_logical_type_date_with_default():
    name = "a date"
    python_type = datetime.date
    field = AvroField(name, python_type, default=consts.now.date())
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: consts.now.date())

    date_time = datetime.datetime.combine(consts.now, datetime.datetime.min.time())
    ts = (date_time - datetime.datetime(1970, 1, 1)).total_seconds()

    expected = {
        "name": name,
        "type": {"type": field_utils.INT, "logicalType": field_utils.DATE},
        "default": ts / (3600 * 24),
    }

    assert expected == field.to_dict()
    assert expected == field_with_default_factory.to_dict()


def test_logical_type_time_millis_with_default() -> None:
    name = "a time"
    python_type = datetime.time
    time = consts.now.time()
    field = AvroField(name, python_type, default=time)
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: time)

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
    assert expected == field_with_default_factory.to_dict()


def test_logical_type_time_micros_with_default() -> None:
    name = "a time"
    python_type = types.TimeMicro
    time = consts.now.time()
    field = AvroField(name, python_type, default=time)
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: time)

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

    assert expected == field.to_dict()
    assert expected == field_with_default_factory.to_dict()


def test_logical_type_datetime_micros_with_default() -> None:
    name = "a datetime"
    python_type = types.DateTimeMicro
    field = AvroField(name, python_type, default=consts.now)
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: consts.now)

    ts = consts.now.timestamp()

    expected = {
        "name": name,
        "type": {"type": field_utils.LONG, "logicalType": field_utils.TIMESTAMP_MICROS},
        "default": ts * 1000000,
    }

    assert expected == field.to_dict()
    assert expected == field_with_default_factory.to_dict()


def test_logical_type_datetime_with_default() -> None:
    name = "a datetime"
    python_type = datetime.datetime
    field = AvroField(name, python_type, default=consts.now)
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: consts.now)

    ts = consts.now.timestamp()

    expected = {
        "name": name,
        "type": {"type": field_utils.LONG, "logicalType": field_utils.TIMESTAMP_MILLIS},
        "default": int(ts * 1000),
    }

    assert expected == field.to_dict()
    assert expected == field_with_default_factory.to_dict()


def test_logical_type_timedelta_with_default() -> None:
    name = "a timedelta"
    python_type = datetime.timedelta
    delta = datetime.timedelta(seconds=1.234567)
    seconds = delta.total_seconds()

    field = AvroField(name, python_type, default=delta)
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: delta)

    expected = {
        "name": name,
        "type": {"type": field_utils.DOUBLE, "logicalType": field_utils.TIMEDELTA},
        "default": seconds,
    }

    assert expected == field.to_dict()
    assert expected == field_with_default_factory.to_dict()


@pytest.mark.parametrize(
    "python_type,avro_type",
    (
        (uuid.uuid4, {"type": field_utils.STRING, "logicalType": field_utils.UUID}),
        (uuid.UUID, {"type": field_utils.STRING, "logicalType": field_utils.UUID}),
        # pydantic fields
        (
            pydantic.UUID1,
            {
                "type": field_utils.STRING,
                "logicalType": field_utils.UUID,
                "pydantic-class": "UUID1",
            },
        ),
        (
            pydantic.UUID3,
            {
                "type": field_utils.STRING,
                "logicalType": field_utils.UUID,
                "pydantic-class": "UUID3",
            },
        ),
        (
            pydantic.UUID4,
            {
                "type": field_utils.STRING,
                "logicalType": field_utils.UUID,
                "pydantic-class": "UUID4",
            },
        ),
        (
            pydantic.UUID5,
            {
                "type": field_utils.STRING,
                "logicalType": field_utils.UUID,
                "pydantic-class": "UUID5",
            },
        ),
    ),
)
def test_logical_type_uuid_with_default(python_type, avro_type) -> None:
    name = "a uuid"
    default = uuid.UUID("d793fc4f-2eef-440a-af8b-a8e884d7b1a8")
    field = AvroField(name, python_type, default=default)
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: default)
    field.to_dict()

    expected = {
        "name": name,
        "type": avro_type,
        "default": str(default),
    }

    assert expected == field.to_dict()
    assert expected == field_with_default_factory.to_dict()


@pytest.mark.parametrize("logical_type,invalid_default,msg", consts.LOGICAL_TYPES_AND_INVALID_DEFAULTS)
def test_invalid_default_values(logical_type, invalid_default, msg):
    name = "a_field"
    field = AvroField(name, logical_type, default=invalid_default)

    msg = msg or f'Invalid default type {type(invalid_default)} for field "{name}". Default should be {logical_type}'
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
    field = AvroField(name, python_type, default=default)
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: default)

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
    assert expected == field_with_default_factory.to_dict()

    # Use types.Decimal to set explicitly
    python_type = types.condecimal(max_digits=7, decimal_places=5)
    field = AvroField(name, python_type)

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
    field = AvroField(name, python_type, default=decimal.Decimal("3.14"))
    field_with_default_factory = AvroField(name, python_type, default_factory=lambda: decimal.Decimal("3.14"))

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
    assert expected == field_with_default_factory.to_dict()

    python_type = types.condecimal(max_digits=7, decimal_places=5)
    field = AvroField(name, python_type, default=None)

    expected = {
        "name": name,
        "type": [
            "null",
            {"type": "bytes", "logicalType": "decimal", "precision": 7, "scale": 5},
        ],
        "default": None,
    }

    assert expected == field.to_dict()

    # Validate 0 <= scale <= precision
    with pytest.raises(
        ValueError,
        match="`decimal_places` must be zero or a positive integer less than or equal to the precision.",
    ):
        python_type = types.condecimal(max_digits=1, decimal_places=-1)
        field = AvroField(name, python_type)

        field.to_dict()

    # Validate 0 <= scale <= precision
    with pytest.raises(
        ValueError,
        match="`decimal_places` must be zero or a positive integer less than or equal to the precision.",
    ):
        python_type = types.condecimal(max_digits=1, decimal_places=3)
        field = AvroField(name, python_type)

        field.to_dict()

    # Validate precision >= 0
    with pytest.raises(ValueError, match="`max_digits` must be a positive integer greater than zero"):
        python_type = types.condecimal(max_digits=-1, decimal_places=2)
        field = AvroField(name, python_type)

        field.to_dict()

    # Catch unexpected default value for decimal.Decimal
    with pytest.raises(ValueError):
        default = 7
        field = AvroField(name, python_type, default=default)

        field.to_dict()

    # Default decimal.Decimal has more digits than listed precision
    with pytest.raises(ValueError):
        python_type = types.condecimal(max_digits=3, decimal_places=2)
        field = AvroField(name, python_type, default=decimal.Decimal("3.14159"))

        field.to_dict()

    # Default decimal.Decimal has more digits past decimal than scale
    with pytest.raises(ValueError):
        python_type = types.condecimal(max_digits=3, decimal_places=1)
        field = AvroField(name, python_type, default=decimal.Decimal("3.14"))

        field.to_dict()

    # Just for code coverage
    with pytest.raises(ValueError):
        python_type = types.condecimal(max_digits=3, decimal_places=1)
        field = AvroField(name, python_type, default=decimal.Decimal("3.14"))

        field.to_dict()
