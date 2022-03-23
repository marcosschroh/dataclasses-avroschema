## Complex Types

The following list represent the avro complex types mapped to python types:

| Avro Type          | Python Type                                                        |
| ------------------ | ------------------------------------------------------------------ |
| enums              | enum.Enum                                                         |
| arrays             | typing.List, typing.Tuple, typing.Sequence, typing.MutableSequence |
| maps               | typing.Dict, typing.Mapping, typing.MutableMapping                 |
| fixed              | types.Fixed                                                        |
| unions             | typing.Union                                                       |
| unions with `null` | typing.Optional                                                    |
| records            | Python Class                                                       |

### Enums

Example:

```python
import enum

from dataclasses_avroschema import AvroModel


class FavoriteColor(enum.Enum):
    BLUE = "Blue"
    YELLOW = "Yellow"
    GREEN = "Green"
    
    class Meta:
        doc = "A favorite color"
        namespace = "some.name.space"
        aliases = ["Color", "My favorite color"]

class User(AvroModel):
    "An User"
    favorite_color: FavoriteColor = FavoriteColor.BLUE


User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields":
  [
    {
      "name": "favorite_color",
      "type":
      {
        "type": "enum",
        "name": "favorite_color",
        "symbols":
        [
          "Blue",
          "Yellow",
          "Green"
        ],
        "doc": "A favorite color",
        "namespace": "some.name.space",
        "aliases":
        ["Color", "My favorite color"]
      },
      "default": "Blue"
    }
  ],
  "doc": "An User"
}'
```

### Arrays

Example:

```python
import dataclasses

import typing

from dataclasses_avroschema import AvroModel


class UserAdvance(AvroModel):
    "User advanced"
    pets: typing.List[str]
    cars: typing.List[str] = None
    favourites_numbers: typing.List[int] = dataclasses.field(default_factory=lambda: [7, 13])


UserAdvance.avro_schema()

'{
  "type": "record",
  "name": "UserAdvance",
  "fields": [
    {
      "name": "pets",
      "type": {
        "type": "array",
        "items": "string",
        "name": "pet"
      }
    },
    {
      "name": "cars",
      "type": {
        "type": "array",
        "items": "string",
        "name": "car"
      },
      "default": []
    },
    {
      "name": "favourites_numbers",
      "type": {
        "type": "array",
        "items": "long",
        "name": "favourites_number"
      },
      "default": [7, 13]
    }
  ],
  "doc": "User advanced"
}'
```

### Maps

Example:

```python
import dataclasses

import typing

from dataclasses_avroschema import AvroModel


class UserAdvance(AvroModel):
    "User advanced"
    accounts_money: typing.Dict[str, float]
    cars_brand_total: typing.Dict[str, int] = None
    family_ages: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"father": 50})

UserAdvance.avro_schema()

'{
  "type": "record",
  "name": "UserAdvance",
  "fields": [
    {
      "name": "accounts_money",
      "type": {
        "type": "map",
        "values": "float",
        "name": "accounts_money"
      }
    },
    {
      "name": "cars_brand_total",
      "type": {
        "type": "map",
        "values": "long",
        "name": "cars_brand_total"
      },
      "default": {}
    },
    {
      "name": "family_ages",
      "type": {
        "type": "map",
        "values": "long",
        "name": "family_age"
      },
      "default": {"father": 50}
    }
  ],
  "doc": "User advanced"
}'
```

### Fixed

```python
import typing

from dataclasses_avroschema import AvroModel, types


class UserAdvance(AvroModel):
    name: str
    md5: types.Fixed = types.Fixed(16, namespace='md5', aliases=["md5", "hash"])

UnionSchema.avro_schema()

{
  'type': 'record',
  'name': 'UserAdvance',
  'fields': [
    {'name': 'name', 'type': 'string'},
    {'name': 'md5', 'type': {'type': 'fixed', 'name': 'md5', 'size': 16,'namespace': 'md5', 'aliases': ['md5', 'hash']}}
  ],
  'doc': 'UserAdvance(name: str, md5: dataclasses_avroschema.types.Fixed = 16)'}
```

### Unions

```python
import typing
import dataclasses
import datetime
import uuid

from dataclasses_avroschema import AvroModel

class UnionSchema(AvroModel):
    "Some Unions"
    first_union: typing.Union[str, int]
    logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
    second_union: typing.Union[str, int] = dataclasses.field(
    default_factory=lambda: ["test"])
    third_union: typing.Union[int, str] = 'STRING TYPE'

UnionSchema.avro_schema()

{
  "type": "record",
  "name": "UnionSchema",
  "fields": [
  {"name": "first_union", "type": ["string", "long"]},
  {"name": "logical_union", "type": [
    {"type": "long", "logicalType": "timestamp-millis"},
    {"type": "long", "logicalType": "date"},
    {"type": "string", "logicalType": "uuid"}]},
  {"name": "second_union", "type": ["string", "long"], "default": ["test"]},
  {"name": "third_union", "type": ["string", "long"], "default": "STRING TYPE"}],
  "doc": "Some Unions"
}

# Union with Records

class Bus(AvroModel):
    "A Bus"
    engine_name: str


class Car(AvroModel):
    "A Car"
    engine_name: str


 class UnionSchema(AvroModel):
    "Some Unions"
    lake_trip: typing.Union[Bus, Car]
    river_trip: typing.Union[Bus, Car] = None
    mountain_trip: typing.Union[Bus, Car] = dataclasses.field(
        default_factory=lambda: {"engine_name": "honda"})

UnionSchema.avro_schema()

'{
  "type": "record",
  "name": "UnionSchema",
  "fields": [
    {
      "name": "lake_trip",
      "type": [
        {
          "type": "record",
          "name": "Bus",
          "fields": [
            {
              "name": "engine_name",
              "type": "string"
            }
          ],
          "doc": "A Bus"
        },
        {
          "type": "record",
          "name": "Car",
          "fields": [
            {
              "name": "engine_name",
              "type": "string"
            }
          ],
          "doc": "A Car"
        }
      ]
    },
    {
      "name": "river_trip",
      "type": [
        "null",
        {
          "type": "record",
          "name": "Bus",
          "fields": [
            {
              "name": "engine_name",
              "type": "string"
            }
          ],
          "doc": "A Bus"
        },
        {
          "type": "record",
          "name": "Car",
          "fields": [
            {
              "name": "engine_name",
              "type": "string"
            }
          ],
          "doc": "A Car"
        }
      ],
      "default": null
    },
    {
      "name": "mountain_trip",
      "type": [
        {
          "type": "record",
          "name": "Bus",
          "fields": [
            {
              "name": "engine_name",
              "type": "string"
            }
          ],
          "doc": "A Bus"
        },
        {
          "type": "record",
          "name": "Car",
          "fields": [
            {
              "name": "engine_name",
              "type": "string"
            }
          ],
          "doc": "A Car"
        }
      ],
      "default": {"engine_name": "honda"}
    }
  ],
  "doc": "Some Unions"
}'
```

### Unions with typing.Optional

`typing.Optional[Any]` is translated as an optional Union: `typing.Union[Any, NoneType]` where `NoneType`
is always at the end

```python
import typing
import dataclasses

from dataclasses_avroschema import AvroModel
from dataclasses import dataclass, field

@dataclasses.dataclass
class X(AvroModel):
    y: typing.Optional[typing.List[int]]


X.avro_schema()

'{
    "type": "record",
    "name": "X",
    "fields": [
        {"name": "y", "type": [{"type": "array", "items": "long", "name": "y"}, "null"]}
    ],
    "doc": "X(y: Union[List[int], NoneType])"
}'
```
