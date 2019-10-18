## Complex Types

The following list represent the avro complext types mapped to python types:

| Avro Type | Python Type |
|-----------|-------------|
| enums     |   tuple     |
| arrays    |   list      |
| maps      |   dict      |
| unions    |typing.Union |
| records   |Python Class |


### Enums

Example:

```python
import typing

from dataclasses_avroschema.schema_generator import SchemaGenerator


class User:
    "An User"
    favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")

SchemaGenerator(User).avro_schema()


'{
  "type": "record",
  "name": "User",
  "fields": [
    {
      "name": "favorite_colors",
      "type": {
        "type": "enum",
        "symbols": ["BLUE", "YELLOW", "GREEN"],
        "name": "favorite_color"
      }
    }
  ],
  "doc": "An User"
}'
```

### Arrays

Example:

```python
import typing
import dataclasses

from dataclasses_avroschema.schema_generator import SchemaGenerator


class UserAdvance:
    "User advanced"
    pets: typing.List[str]
    cars: typing.List[str] = None
    favourites_numbers: typing.List[int] = dataclasses.field(default_factory=lambda: [7, 13])


SchemaGenerator(UserAdvance).avro_schema()

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
        "items": "int",
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
import typing
import dataclasses

from dataclasses_avroschema.schema_generator import SchemaGenerator


class UserAdvance:
    "User advanced"
    accounts_money: typing.Dict[str, float]
    cars_brand_total: typing.Dict[str, int] = None
    family_ages: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"father": 50}) 

SchemaGenerator(UserAdvance).avro_schema()

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
        "values": "int",
        "name": "cars_brand_total"
      },
      "default": {}
    },
    {
      "name": "family_ages",
      "type": {
        "type": "map",
        "values": "int",
        "name": "family_age"
      },
      "default": {"father": 50}
    }
  ],
  "doc": "User advanced"
}'
```

### Records

Mapped as a Python class

There are some special avro attributes like `aliases`, `namespace` and `doc` (both not required) that can be specified in a record type.

The `doc` attribute can be set via the docstring class. The `aliases` and `namespaces` must be set using the `extra_avro_attributes` static method.

```python
from dataclasses_avroschema.schema_generator import SchemaGenerator


class User:
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    def extra_avro_attributes() -> typing.Dict[str, typing.Any]:
        return {
            "namespace": "test.com.ar/user/v1",
            "aliases": ["User", "My favorite User"]
        }

SchemaGenerator(User).avro_schema()

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
      "name": "has_pets",
      "type": ["boolean", "null"],
      "default": false
    },
    {
      "name": "money",
      "type": ["float", "null"],
      "default": 100.3
    }
  ],
  "doc": "My User Class",
  "namespace": "test.com.ar/user/v1",
  "aliases": ["User", "My favorite User"]
}'
```

### Unions

```python
import typing
import dataclasses

from dataclasses_avroschema.schema_generator import SchemaGenerator


class Bus:
    "A Bus"
    engine_name: str


class Car:
    "A Car"
    engine_name: str


 class UnionSchema:
    "Some Unions"
    lake_trip: typing.Union[Bus, Car]
    river_trip: typing.Union[Bus, Car] = None
    mountain_trip: typing.Union[Bus, Car] = dataclasses.field(
        default_factory=lambda: {"engine_name": "honda"})

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
      "default": "null"
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
