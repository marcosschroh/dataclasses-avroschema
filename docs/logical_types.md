# Logical Types

The following list represent the avro logical types mapped to python types:

| Avro Type | Logical Type |Python Type |
|-----------|--------------|-------------|
| int       |  date        | datetime.date |
| int       |  time-millis | datetime.time     |
| long      |  time-micros | types.TimeMicro |
| long      |  timestamp-millis | datetime.datetime |
| long      |  timestamp-micros | types.DateTimeMicro |
| string    |  uuid        | uuid.uuid4 |
| string    |  uuid        | uuid.UUID |
| bytes     | decimal      | types.condecimal |

!!! note
    Custom `logicalTypes` are not supported

## Date

```python title="Date example"
import datetime
import dataclasses
import typing

from dataclasses_avroschema import AvroModel

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)


@dataclasses.dataclass
class DateLogicalType(AvroModel):
    "Date type"
    birthday: datetime.date
    meeting_date: typing.Optional[datetime.date] = None
    release_datetime: datetime.date = a_datetime.date()


DateLogicalType.avro_schema()

'{
  "type": "record",
  "name": "DateLogicalType",
  "fields": [
    {
      "name": "birthday",
      "type": {"type": "int", "logicalType": "date"}},
    {
      "name": "meeting_date",
      "type": ["null", {"type": "int", "logicalType": "date"}],
      "default": null
    },
    {
      "name": "release_datetime",
      "type": {"type": "int", "logicalType": "date"},
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
import typing

from dataclasses_avroschema import AvroModel, TimeMicro

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)


@dataclasses.dataclass
class TimeLogicalTypes(AvroModel):
    "Time logical types"
    birthday_time: datetime.time
    meeting_time: typing.Optional[datetime.time] = None
    release_time: datetime.time = a_datetime.time()
    release_time_micro: TimeMicro = a_datetime.time()

TimeLogicalTypes.avro_schema()

'{
  "type": "record",
  "name": "TimeLogicalTypes",
  "fields": [
    {
      "name": "birthday_time",
      "type": {"type": "int", "logicalType": "time-millis"}
    },
    {
      "name": "meeting_time",
      "type": ["null", {"type": "int", "logicalType": "time-millis"}],
      "default": null
    },
    {
      "name": "release_time",
      "type": {"type": "int", "logicalType": "time-millis"},
      "default": 64662000
    },
    {
      "name": "release_time_micro",
      "type": {"type": "long", "logicalType": "time-micros"},
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
import typing

from dataclasses_avroschema import AvroModel, DateTimeMicro

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)


@dataclasses.dataclass
class DatetimeLogicalType(AvroModel):
    "Datetime logical types"
    birthday: datetime.datetime
    meeting_time: typing.Optional[datetime.datetime] = None
    release_datetime: datetime.datetime = a_datetime
    release_datetime_micro: DateTimeMicro = a_datetime

DatetimeLogicalType.avro_schema()

'{
  "type": "record",
  "name": "DatetimeLogicalType",
  "fields": [
    {
      "name": "birthday",
      "type": {"type": "long", "logicalType": "timestamp-millis"}
    },
    {
      "name": "meeting_time",
      "type": ["nul", {"type": "long", "logicalType": "timestamp-millis"}],
      "default": null
    },
    {
      "name": "release_datetime",
      "type": {"type": "long", "logicalType": "timestamp-millis"},
      "default": 1570903062000
    },
    {
      "name": "release_datetime_micro",
      "type": {"type": "long", "logicalType": "timestamp-micros"},
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
import typing

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class UUIDLogicalTypes(AvroModel):
    "UUID logical types"
    uuid_1: uuid.uuid4
    uuid_2: typing.Optional[uuid.uuid4] = None
    event_uuid: uuid.uuid4 = uuid.uuid4()

UUIDLogicalTypes.avro_schema()

'{
  "type": "record",
  "name": "UUIDLogicalTypes",
  "fields": [
    {
      "name": "uuid_1",
      "type": {"type": "string", "logicalType": "uuid"}
    },
    {
      "name": "uuid_2",
      "type": ["null", {"type": "string", "logicalType": "uuid"}],
      "default": null
    },
    {
      "name": "event_uuid",
      "type": {"type": "string", "logicalType": "uuid"},
      "default": "ad0677ab-bd1c-4383-9d45-e46c56bcc5c9"
    }
  ],
  "doc": "UUID logical types"
}'
```

*(This script is complete, it should run "as is")*

## Decimal

`Decimal` types in `avro` must specify two required attributes: `precision` and `scale`. `Precision` represents the amount of digits and `scale` the amount of decimal places.
Because with the python type `decimal.Decimal` is not possible to supply the required arguments, `dataclasses-avroschema` provides a funtion to create the decimals.
The function `types.condecimal` annotates the `decimal.Decimal` type and it adds the required attibutes.

### Arguments to condecimal

The following arguments are available when using the condecimal type function

- max_digits (int): total number digits
- decimal_places (int): total decimal places

```python title="Decimal example"
import decimal
import dataclasses
import typing

from dataclasses_avroschema import AvroModel, types


@dataclasses.dataclass
class DecimalLogicalTypes(AvroModel):
    "Decimal logical types"
    money: types.condecimal(max_digits=3, decimal_places=2)
    decimal_with_default: types.condecimal(max_digits=3, decimal_places=2) = decimal.Decimal('3.14')
    optional_decimal: typing.Optional[types.condecimal(max_digits=3, decimal_places=2)] = None

DecimalLogicalTypes.avro_schema()

'{
  "type": "record",
  "name": "DecimalLogicalTypes",
  "fields": [
    {
      "name": "money",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 3,
        "scale": 2
      }
    },
    {
      "name": "decimal_with_default",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 3,
        "scale": 2
      },
      "default": "\\u013a"
    },
    {
      "name": "optional_decimal",
      "type": [
        "null",
        {
          "type": "bytes",
          "logicalType": "decimal",
          "precision": 3,
          "scale": 2
        }
      ]
      "default": "null"
    }
  ],
  "doc": "Decimal logical types"
}'
```

*(This script is complete, it should run "as is")*
