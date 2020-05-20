## Schema with Logical Types

The following list represent the avro logical types mapped to python types:

| Avro Type | Logical Type |Python Type |
|-----------|--------------|-------------|
| int       |  date        | datetime.date
| int       |  time-millis | datetime.time     |
| long      |  timestamp-millis | datetime.datetime |
| string    |  uuid        | uuid.uuid4 |

### Date

```python
import datetime

from dataclasses_avroschema.schema_generator import SchemaGenerator

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)

class DateLogicalType:
    "Date type"
    birthday: datetime.date
    meeting_date: datetime.date = None
    release_datetime: datetime.date = a_datetime.date()


SchemaGenerator(DateLogicalType).avro_schema()

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
      "default": "null"
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

### Time

```python
import datetime

from dataclasses_avroschema.schema_generator import SchemaGenerator

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)


class TimeLogicalTypes:
    "Time logical types"
    birthday_time: datetime.time
    meeting_time: datetime.time = None
    release_time: datetime.time = a_datetime.time()

SchemaGenerator(TimeLogicalTypes).avro_schema()

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
      "default": "null"
    },
    {
      "name": "release_time",
      "type": {
        "type": "int",
        "logicalType": "time-millis"
      },
      "default": 64662000
    }
  ],
  "doc": "Time logical types"
}'
```

### Datetime

```python
import datetime

from dataclasses_avroschema.schema_generator import SchemaGenerator

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)

class DatetimeLogicalType:
    "Datetime logical types"
    birthday: datetime.datetime
    meeting_time: datetime.datetime = None
    release_datetime: datetime.datetime = a_datetime

SchemaGenerator(DatetimeLogicalType).avro_schema()

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
      "default": "null"
    },
    {
      "name": "release_datetime",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "default": 1570903062000.0
    }
  ],
  "doc": "Datetime logical types"
}'
```

### UUID

```python
import uuid

from dataclasses_avroschema.schema_generator import SchemaGenerator


class UUIDLogicalTypes:
    "UUID logical types"
    uuid_1: uuid.uuid4
    uuid_2: uuid.uuid4 = None
    event_uuid: uuid.uuid4 = uuid.uuid4()

SchemaGenerator(UUIDLogicalTypes).avro_schema()

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
      },"default": "null"
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
