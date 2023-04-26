# Faust integration

This library also has support to generate `Avro Schemas` from a `faust.Record` using `AvroRecord`.
`AvroRecord` is just a class that inherits from `faust.Record` and `AvroModel` respectively.

!!! note
    All the AvroModel features like `serialization`, `parsing objects`, `validation` and `fake`, are available with AvroRecord

Example:

```python title="Basic usage"
import dataclasses
import typing

from dataclasses_avroschema.faust import AvroRecord


@dataclasses.dataclass
class UserAdvance(AvroRecord):
    name: str
    age: int
    pets: typing.List[str] = dataclasses.field(default_factory=lambda: ['dog', 'cat'])
    accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
    has_car: bool = False
    favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
    country: str = "Argentina"
    address: typing.Optional[str] = None

    class Meta:
        schema_doc = False


UserAdvance.avro_schema()
```

resulting in

```json
{
  "type": "record",
  "name": "UserAdvance",
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
        "values": "long",
        "name": "account"
      },
      "default": {"key": 1}
    },
    {
      "name": "has_car",
      "type": "boolean",
      "default": false
    },
    {
      "name": "favorite_colors", 
      "type": {
        "type": "array", "items": "string", "name": "favorite_color"
      }
    },
    {
      "name": "country",
      "type": "string",
      "default": "Argentina"
    },
    {
      "name": "address",
      "type": ["null", "string"],
      "default": null
    }
  ]
}
```

*(This script is complete, it should run "as is")*
