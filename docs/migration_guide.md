## Migration from previous versions to 0.23.0

1. Now the name for Nested record uses the `class.__name__` instead of ``class.__name__.lower()_record`.

having this schemas:

```python
class Address(AvroModel):
    "An Address"
    street: str
    street_number: int


class User(AvroModel):
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.Dict[str, Address]


# PREVIOUS
User.avro_schema()
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "addresses", "type": {
        "type": "map",
        "values": {
          "type": "record",
          "name": "address_record",
          "fields": [
            {"name": "street", "type": "string"},
            {"name": "street_number", "type": "long"}
          ],
          "doc": "An Address"
        },
        "name": "address"
      }
    }
  ],
  "doc": "User with multiple Address"
}


# VERSIONS 0.23.0
User.avro_schema()
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "addresses", "type": {
        "type": "map",
        "values": {
          "type": "record",
          "name": "Address",
          "fields": [
            {"name": "street", "type": "string"},
            {"name": "street_number", "type": "long"}
          ],
          "doc": "An Address"
        },
        "name": "address"
      }
    }
  ],
  "doc": "User with multiple Address"
}
```

2. Now we use `namespaces` when same types are referenced multiple times (DRY), so you *MUST* define the property `namespace`:

```python
class Location(AvroModel):
    latitude: float
    longitude: float

    class Meta:
        namespace = "types.location_type"  # REQUIRED!!!!

class Trip(AvroModel):
    start_time: datetime.datetime
    start_location: Location
    finish_time: datetime.datetime
    finish_location: Location

Trip.avro_schema_to_python()
```

```json
{
  "type": "record",
  "name": "Trip",
  "fields": [
    {
      "name": "start_time",
      "type": {"type": "long", "logicalType": "timestamp-millis"}
    },
    {
      "name": "start_location",
      "type": {"type": "record",
      "name": "Location",
        "fields": [
          {"name": "latitude", "type": "double"},
          {"name": "longitude", "type": "double"}
        ],
      "doc": "Location(latitude: float, longitude: float)",
      "namespace": "types.location_type"}},
    {
      "name": "finish_time",
      "type": {"type": "long", "logicalType": "timestamp-millis"}
    },
    {
      "name": "finish_location", "type": "types.location_type.Location"  // using the namespace
    }
  ],
  "doc": "Trip(start_time: datetime.datetime, start_location: __main__.Location, finish_time: datetime.datetime, finish_location: __main__.Location)"
}
```

## Migration from previous versions to 0.14.0

Now all the dataclasses should inheritance from `AvroModel` and not use anymore the `SchemaGenerator`:

```python
# Versions < 0.14.0

import typing

from dataclasses_avroschema import SchemaGenerator, types


class User:
    "An User"
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"])
    country: str = "Argentina"
    address: str = None

SchemaGenerator(User).avro_schema()

# New versions
from dataclasses_avroschema import AvroModel, types


class User(AvroModel):
    "An User"
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"])
    country: str = "Argentina"
    address: str = None

User.avro_schema()
```

Another changes introduced was the way that extra avro attributes are represented, like `namespace`, `aliases` and whether to include `avro documentation`:

```python
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

SchemaGenerator(User, include_schema_doc=False).avro_schema()

# Now is perform using a Meta class

class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    class Meta:
        schema_doc = False
        namespace = "test.com.ar/user/v1"
        aliases = ["User", "My favorite User"]
```
