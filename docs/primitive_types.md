## Primitive Types

The following list represent the avro primitive types mapped to python types:

| Avro Type | Python Type |
|-----------|-------------|
| string    |     str     |
| int       |     int     |
| boolean   |     bool    |
| float     |     float   |
| null      |     None    |
| bytes     |     wip     |


Example:

```python
from dataclasses_avroschema import AvroModel


class User(AvroModel):
    "An User"
    name: str
    age: int
    is_student: bool
    money_available: float


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
      "type": "int"
    },
    {
      "name": "is_student",
      "type": "boolean"
    },
    {
      "name": "money_available",
      "type": "float"
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


User.avro_schema()

# We can see the use of null in the schema generated:

'{
  "type": "record",
  "name": "User",
  "fields": [
    {
      "name": "name",
      "type": ["null", "string"],
      "default": "null"
    },
    {
      "name": "age",
      "type": ["null", "int"],
      "default": "null"
    },
    {
      "name": "is_student",
      "type": ["null", "boolean"],
      "default": "null"
    },
    {
      "name": "money_available",
      "type": ["null", "float"],
      "default": "null"}
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


User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {
      "name": "name",
      "type": ["string", "null"],
      "default": "Juan"
    },
    {
      "name": "age",
      "type": ["int", "null"],
      "default": 20
    },
    {
      "name": "is_student",
      "type": ["boolean", "null"],
      "default": true
    },
    {
      "name": "money_available",
      "type": ["float", "null"],
      "default": 100.2
    }
  ],
  "doc": "An User"
}'
```
