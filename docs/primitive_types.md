# Primitive Types

The following list represent the avro primitive types mapped to python types:

| Avro Type    | Python Type |
|--------------|-------------|
| string       |     str     |
| int,long     |     int     |
| boolean      |     bool    |
| float,double |     float   |
| null         |     None    |
| bytes        |     bytes   |

## Examples

```python title="Primitive types"
import dataclasses

from dataclasses_avroschema import AvroModel, types


@dataclasses.dataclass
class User(AvroModel):
    "An User"
    name: str
    age: int
    height: types.Float32
    weight: types.Int32
    is_student: bool
    money_available: float
    encoded: bytes


User.avro_schema()
```

*(This script is complete, it should run "as is")*

```json
{
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
      "name": "height",
      "type": "float"
    },
    {
      "name": "weight",
      "type": "int"
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
}
```

## Examples with `null`

```python
import dataclasses
from typing import Optional

from dataclasses_avroschema import AvroModel, types


@dataclasses.dataclass
class User(AvroModel):
    "An User"
    name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[types.Float32] = None
    weight: Optional[types.Int32] = None
    is_student: Optional[bool] = None
    money_available: Optional[float] = None
    encoded: Optional[bytes] = None


User.avro_schema()
```

*(This script is complete, it should run "as is")*

```json
{
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
      "name": "height",
      "type": ["null", "float"],
      "default": null
    },
    {
      "name": "weight",
      "type": ["null", "int"],
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
}
```

*(This script is complete, it should run "as is")*

## Examples with default values

```python
import dataclasses

from dataclasses_avroschema import AvroModel, types


@dataclasses.dataclass
class User(AvroModel):
    "An User"
    name: str = 'Juan'
    age: int = 20
    height: types.Float32 = 165.3
    weight: types.Int32 = 72
    is_student: bool = True
    money_available: float = 100.2
    encoded: bytes = b"hi"


User.avro_schema()
```

*(This script is complete, it should run "as is")*

```json
{
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
      "name": "height",
      "type": ["null", "float"],
      "default": 165.3
    },
    {
      "name": "weight",
      "type": ["null", "int"],
      "default": 72
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
}
```

*(This script is complete, it should run "as is")*
