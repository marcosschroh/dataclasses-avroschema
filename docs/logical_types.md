# Logical Types

The following list represent the avro logical types mapped to python types:

| Avro Type | Logical Type |Python Type |
|-----------|--------------|-------------|
| int       |  date        | datetime.date
| int       |  time-millis | datetime.time     |
| long      |  time-micros | types.TimeMicro |
| long      |  timestamp-millis | datetime.datetime |
| long      |  timestamp-micros | types.DateTimeMicro |
| string    |  uuid        | uuid.uuid4 |
| string    |  uuid        | uuid.UUID |
| bytes     | decimal      | decimal.Decimal

## Date

```python title="Date example"
import datetime
import dataclasses

from dataclasses_avroschema import AvroModel

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)


@dataclasses.dataclass
class DateLogicalType(AvroModel):
    "Date type"
    birthday: datetime.date
    meeting_date: datetime.date = None
    release_datetime: datetime.date = a_datetime.date()


DateLogicalType.avro_schema()

'{
  "type": "record",
  "name": "DateLogicalType",
  "fields": [
    {
      "name": "birthday",
      "type": {
        "type": "int",
        "logicalType": "date"
      }
    },
    {
      "name": "meeting_date",
      "type": {
        "type": "int",
        "logicalType": "date"
      },
      "default": null
    },
    {
      "name": "release_datetime",
      "type": {
        "type": "int",
        "logicalType": "date"
      },
      "default": 18181
    }
  ],
  "doc": "Date type"
}'
```

*(This script is complete, it should run "as is")*

## Time

```python title="Time example"
import datetime
import dataclasses

from dataclasses_avroschema import AvroModel, TimeMicro

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)


@dataclasses.dataclass
class TimeLogicalTypes(AvroModel):
    "Time logical types"
    birthday_time: datetime.time
    meeting_time: datetime.time = None
    release_time: datetime.time = a_datetime.time()
    release_time_micro: TimeMicro = a_datetime.time()

TimeLogicalTypes.avro_schema()

'{
  "type": "record",
  "name": "TimeLogicalTypes",
  "fields": [
    {
      "name": "birthday_time",
      "type": {
        "type": "int",
        "logicalType": "time-millis"
      }
    },
    {
      "name": "meeting_time",
      "type": {
        "type": "int",
        "logicalType": "time-millis"
      },
      "default": null
    },
    {
      "name": "release_time",
      "type": {
        "type": "int",
        "logicalType": "time-millis"
      },
      "default": 64662000
    },
    {
      "name": "release_time_micro",
      "type": {
        "type": "long",
        "logicalType": "time-micros"
      },
      "default": 64662000000
    }
  ],
  "doc": "Time logical types"
}'
```

*(This script is complete, it should run "as is")*

!!! nore annotate "To use `time-micros` in avro schemas you need to use `types.TimeMicro`"

## Datetime

```python title="DateTime example"
import datetime
import dataclasses

from dataclasses_avroschema import AvroModel, DateTimeMicro

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)


@dataclasses.dataclass
class DatetimeLogicalType(AvroModel):
    "Datetime logical types"
    birthday: datetime.datetime
    meeting_time: datetime.datetime = None
    release_datetime: datetime.datetime = a_datetime
    release_datetime_micro: DateTimeMicro = a_datetime

DatetimeLogicalType.avro_schema()

'{
  "type": "record",
  "name": "DatetimeLogicalType",
  "fields": [
    {
      "name": "birthday",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "meeting_time",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "default": null
    },
    {
      "name": "release_datetime",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "default": 1570903062000
    },
    {
      "name": "release_datetime_micro",
      "type": {
        "type": "long",
        "logicalType": "timestamp-micros"
      },
      "default": 1570903062000000
    }
  ],
  "doc": "Datetime logical types"
}'
```

*(This script is complete, it should run "as is")*

!!! note
    To use `timestamp-micros` in avro schemas you need to use `types.DateTimeMicro`

## UUID

```python title="UUID example"
import uuid
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class UUIDLogicalTypes(AvroModel):
    "UUID logical types"
    uuid_1: uuid.uuid4
    uuid_2: uuid.uuid4 = None
    event_uuid: uuid.uuid4 = uuid.uuid4()

UUIDLogicalTypes.avro_schema()

'{
  "type": "record",
  "name": "UUIDLogicalTypes",
  "fields": [
    {
      "name": "uuid_1",
      "type": {
        "type": "string",
        "logicalType": "uuid"
      }
    },
    {
      "name": "uuid_2",
      "type": {
        "type": "string",
        "logicalType": "uuid"
      },"default": null
    },
    {
      "name": "event_uuid",
      "type": {
        "type": "string",
        "logicalType": "uuid"
      },
      "default": "ad0677ab-bd1c-4383-9d45-e46c56bcc5c9"
    }
  ],
  "doc": "UUID logical types"
}'
```

*(This script is complete, it should run "as is")*

## Decimal

The below code shows an example on how to use decimals. There's a few important things to note:
* A default IS REQUIRED in order to set scale and precision on the Avro schema
* It is strongly recommended to set these explicitly using `types.Decimal(scale=, precision=)`
* They can be set implicitly by using a default `decimal.Decimal`
* If set implicitly, scale and precision will be derived from the default as follows:
```python
    default: decimal.Decimal = decimal.Decimal('3.14')
    sign, digits, exp = default.as_tuple()
    precision = len(digits)
    scale = exp * -1  # Avro schema defines scale as a positive, as_tuple provides negative
```
* This CAN and WILL have strange consequences if not careful, ESPECIALLY if constructing `decimal.Decimal` with a float. For example:
```python
    string_definition: decimal.Decimal = decimal.Decimal('3.14')
    # scale = 2, precision = 3
    float_definition: decimal.Decimal = decimal.Decimal(3.14)
    # scale = 51, precision = 52
```

```python title="Decimal example"
import decimal
import dataclasses

from dataclasses_avroschema import AvroModel, types


@dataclasses.dataclass
class DecimalLogicalTypes(AvroModel):
    "Decimal logical types"
    explicit: decimal.Decimal = types.Decimal(scale=2, precision=3)
    explicit_with_default: decimal.Decimal = types.Decimal(scale=2, precision=3, default=decimal.Decimal('3.14'))
    implicit: decimal.Decimal = decimal.Decimal('3.14') # sets scale = 2, precision = 3, derived from provided default
    # will_error: decimal.Decimal  # THIS WILL ERROR
DecimalLogicalTypes.avro_schema()

'{
  "type": "record",
  "name": "DecimalLogicalTypes",
  "fields": [
    {
      "name": "explicit",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 3,
        "scale": 2
      }
    },
    {
      "name": "explicit_with_default",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 3,
        "scale": 2
      },
      "default": "\\u013a"
    },
    {
      "name": "implicit",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 3,
        "scale": 2
      },
      "default": "\\u013a"
    }
  ],
  "doc": "Decimal logical types"
}'
```

*(This script is complete, it should run "as is")*
