The following list represent the avro primitive types mapped to python types:

| Avro Type | Python Type |
|-----------|-------------|
| string    |     str     |
| long      |     int     |
| boolean   |     bool    |
| double    |     float   |
| null      |     None    |
| bytes     |     bytes   |


Example:

```python
from dataclasses_avroschema import AvroModel


class User(AvroModel):
    "An User"
    name: str
    age: int
    is_student: bool
    money_available: float
    encoded: bytes


User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {
      "name": "name",
      "type": "string"
    },
    {
      "name": "age",
      "type": "long"
    },
    {
      "name": "is_student",
      "type": "boolean"
    },
    {
      "name": "money_available",
      "type": "double"
    },
    {
        "name": "encoded",
        "type": "bytes"
    }
  ],
  "doc": "An User"
}'
```

Example with defaults:

```python
from dataclasses_avroschema import AvroModel


class User(AvroModel):
    "An User"
    name: str = None
    age: int = None
    is_student: bool = None
    money_available: float = None
    encoded: bytes = None


User.avro_schema()

# We can see the use of null in the schema generated:

'{
  "type": "record",
  "name": "User",
  "fields": [
    {
      "name": "name",
      "type": ["null", "string"],
      "default": null
    },
    {
      "name": "age",
      "type": ["null", "long"],
      "default": null
    },
    {
      "name": "is_student",
      "type": ["null", "boolean"],
      "default": null
    },
    {
      "name": "money_available",
      "type": ["null", "double"],
      "default": null
    },
    {
      "name": "encoded",
      "type": ["null", "bytes"],
      "default": null
    }
  ],
  "doc": "An User"
}'

# Or with null as a second type argument:

class User(AvroModel):
    "An User"
    name: str = 'Juan'
    age: int = 20
    is_student: bool = True
    money_available: float = 100.2
    encoded: bytes = b"hi"


User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {
      "name": "name",
      "type": "string",
      "default": "Juan"
    },
    {
      "name": "age",
      "type": "long",
      "default": 20
    },
    {
      "name": "is_student",
      "type": "boolean",
      "default": true
    },
    {
      "name": "money_available",
      "type": "double",
      "default": 100.2
    },
    {
        "name": "encoded",
        "type": "bytes",
        "default": "hi"
    }
  ],
  "doc": "An User"
}'
```
