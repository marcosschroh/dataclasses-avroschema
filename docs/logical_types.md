## Schema with Logical Types

```python
import datetime
import uuid

from dataclasses_avroschema.schema_generator import SchemaGenerator

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)

class LogicalTypes:
    "Some logical types"
    birthday: datetime.date = a_datetime.date()
    meeting_time: datetime.time = a_datetime.time()
    release_datetime: datetime.datetime = a_datetime
    event_uuid: uuid.uuid4 = uuid.uuid4()

SchemaGenerator(LogicalTypes).avro_schema()

'{
  "type": "record",
  "name": "LogicalTypes",
  "fields": [
    {
      "name": "birthday",
      "type": {
        "type": "int",
        "logicalType": "date"
      },
      "default": 18181
    },
    {
      "name": "meeting_time",
      "type": {
        "type": "int",
        "logicalType": "time-millis"
      },
      "default": 64662000
    },
    {
      "name": "release_datetime",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "default": 1570903062000.0
    },
    {
      "name": "event_uuid",
      "type": {
        "type": "string",
        "logicalType": "uuid"
      },
      "default": "42b8ed8b-ca4a-4d72-91bd-6722c80b9416"
    }
  ],
  "doc": "Some logical types"
}'
```
