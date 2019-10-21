import pytest
import datetime
import uuid

from dataclasses_avroschema import fields


now = datetime.datetime.now()

# Represent the logical types
# (python_type, avro_internal_type, logical_type)
LOGICAL_TYPES_AND_DEFAULTS = (
    (
        datetime.date,
        fields.INT,
        fields.DATE
    ),
    (
        datetime.time,
        fields.INT,
        fields.TIME_MILLIS
    ),
    (
        datetime.datetime,
        fields.LONG,
        fields.TIMESTAMP_MILLIS
    ),
    (
        uuid.uuid4,
        fields.STRING,
        fields.UUID
    )
)

LOGICAL_TYPES_AND_INVALID_DEFAULTS = (
    (datetime.date, 1, None),
    (datetime.time, "test", None),
    (datetime.datetime, 10, None),
    (uuid.uuid4, 10, f"Invalid default type. Default should be {str} or {uuid.UUID}"),
)


@pytest.mark.parametrize("python_type,avro_type,logical_type", LOGICAL_TYPES_AND_DEFAULTS)
def test_logical_types(python_type, avro_type, logical_type):
    name = "a logical type"
    python_type = python_type
    field = fields.Field(name, python_type)

    expected = {
        "name": name,
        "type":  {
            "type": avro_type,
            "logicalType": logical_type
        }
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("python_type,avro_type,logical_type", LOGICAL_TYPES_AND_DEFAULTS)
def test_logical_types_with_null_as_default(python_type, avro_type, logical_type):
    name = "a logical type"
    python_type = python_type
    field = fields.Field(name, python_type, None)

    expected = {
        "name": name,
        "type":  {
            "type": avro_type,
            "logicalType": logical_type
        },
        "default": fields.NULL
    }

    assert expected == field.to_dict()


def test_logical_type_date_with_default():
    name = "a date"
    python_type = datetime.date
    field = fields.Field(name, python_type, now)

    date_time = datetime.datetime.combine(now, datetime.datetime.min.time())
    ts = (date_time - datetime.datetime(1970, 1, 1)).total_seconds()

    expected = {
        "name": name,
        "type":  {
            "type": fields.INT,
            "logicalType": fields.DATE
        },
        "default": ts / (3600 * 24)
    }

    assert expected == field.to_dict()


def test_logical_type_time_with_default():
    name = "a time"
    python_type = datetime.time
    time = now.time()
    field = fields.Field(name, python_type, time)

    hour, minutes, seconds, microseconds = time.hour, time.minute, time.second, time.microsecond
    miliseconds = int((((hour * 60 + minutes) * 60 + seconds) * 1000) + (microseconds / 1000))

    expected = {
        "name": name,
        "type":  {
            "type": fields.INT,
            "logicalType": fields.TIME_MILLIS
        },
        "default": miliseconds
    }

    assert expected == field.to_dict()


def test_logical_type_datetime_with_default():
    name = "a datetime"
    python_type = datetime.datetime
    field = fields.Field(name, python_type, now)

    ts = (now - datetime.datetime(1970, 1, 1)).total_seconds()

    expected = {
        "name": name,
        "type":  {
            "type": fields.LONG,
            "logicalType": fields.TIMESTAMP_MILLIS
        },
        "default": ts * 1000
    }

    assert expected == field.to_dict()


def test_logical_type_uuid_with_default():
    name = "a uuid"
    python_type = uuid.uuid4
    default = uuid.uuid4()
    field = fields.Field(name, python_type, default)

    expected = {
        "name": name,
        "type":  {
            "type": fields.STRING,
            "logicalType": fields.UUID
        },
        "default": str(default)
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("logical_type,invalid_default,msg", LOGICAL_TYPES_AND_INVALID_DEFAULTS)
def test_invalid_default_values(logical_type, invalid_default, msg):
    name = "a_field"
    field = fields.Field(name, logical_type, invalid_default)

    msg = msg or f"Invalid default type. Default should be {logical_type}"
    with pytest.raises(AssertionError, match=msg):
        field.to_dict()
