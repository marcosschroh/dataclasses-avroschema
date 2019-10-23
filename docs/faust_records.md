This library also has support to generate `Avro Schemas` from a `faust.Record`

Example:

```python
import faust
import dataclasses
import typing

from dataclasses_avroschema.schema_generator import SchemaGenerator


class UserAdvance(faust.Record):
    name: str
    age: int
    pets: typing.List[str] = dataclasses.field(default_factory=lambda: ['dog', 'cat'])
    accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
    has_car: bool = False
    favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
    country: str = "Argentina"
    address: str = None


SchemaGenerator(UserAdvance, include_schema_doc=False).avro_schema()

'{
  "type": "record",
  "name": "UserAdvance",
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
      "name": "pets",
      "type": {
        "type": "array",
        "items": "string",
        "name": "pet"
      },
      "default": ["dog", "cat"]
    },
    {
      "name": "accounts",
      "type": {
        "type": "map",
        "values": "int",
        "name": "account"
      },
      "default": {"key": 1}
    },
    {
      "name": "has_car",
      "type": ["boolean", "null"],
      "default": false
    },
    {
      "name": "favorite_colors",
      "type": {
        "type": "enum",
        "symbols": ["BLUE", "YELLOW", "GREEN"],
        "name": "favorite_color"
      }
    },
    {
      "name": "country",
      "type": ["string", "null"],
      "default": "Argentina"
    },
    {
      "name": "address",
      "type": ["null", "string"],
      "default": "null"
    }
  ]
}'
```
