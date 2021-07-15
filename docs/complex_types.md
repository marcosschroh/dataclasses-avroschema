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
from typing import Optional

from dataclasses_avroschema import AvroModel


class FavoriteColor(enum.Enum):
    BLUE = "Blue"
    YELLOW = "Yellow"
    GREEN = "Green"
    
    class Meta:
        doc = "A favorite color"
        namespace = "some.name.space"
        aliases = ["Color", "My favorite color"]
        default = "Green"

class User(AvroModel):
    "An User"
    favorite_color: Optional[FavoriteColor] = None

User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields":
  [
    {
      "name": "favorite_color",
      "type":
      [
        "null",
        {
          "type": "enum",
          "name": "FavoriteColor",
          "symbols": ["Blue", "Yellow", "Green"],
          "doc": "A favorite color",
          "namespace": "some.name.space",
          "aliases": ["Color", "My favorite color"],
          "default": "Green"
        }
      ],
      "default": null
    }
  ],
  "doc": "An User"
}'

```

Note that in addition to a *field-level* default value, you can optionally supply a *type-level* default symbol for the 
enum by supplying the `default` attribute under the `Meta` class. See the 
[Avro specification](https://avro.apache.org/docs/1.10.2/spec.html#Enums) for more details.

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

### Records

Mapped as a Python class

There are some special avro attributes like `aliases`, `namespace` and `doc` (both not required) that can be specified in a record type.

The `doc` attribute can be set via the docstring class. The `aliases` and `namespaces` must be set using the `extra_avro_attributes` static method.

```python
from dataclasses_avroschema import AvroModel


class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    class Meta:
        namespace = "test.com.ar/user/v1"
        aliases = ["User", "My favorite User"]

User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "has_pets", "type": "boolean", "default": false},
    {"name": "money", "type": "double", "default": 100.3}
  ],
  "doc": "My User Class",
  "namespace": "test.com.ar/user/v1",
  "aliases": ["User", "My favorite User"]
}'
```

#### Class Meta

The `class Meta` is used to specify schema attributes that are not represented by the class fields like `namespace`, `aliases` and whether to include the `schema documentation`. One can also provide a custom schema name (the default is the class' name) via `schema_name` attribute and `alias_nested_items` when you have nested items and you want to use custom naming for them.

```python
class Meta:
    schema_name = "Name other than the class name"
    schema_doc = False
    namespace = "test.com.ar/user/v1"
    aliases = ["User", "My favorite User"]
    alias_nested_items = {"address": "Address"}
```

`schema_doc (boolean)`: Whether include the `schema documentation` generated from `docstrings`. Default `True`
`namespace (optional[str])`: Schema namespace. Default `None`
`aliases (optional[List[str]])`: Schema aliases. Default `None`
`alias_nested_items (optional[Dict[str, str]])`: Nested items names
