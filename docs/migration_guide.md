# Migration from previous versions to 0.51.0

- In this version was introduced the namespace `dataclasses_avroschema.pydantic` and the nanespace `dataclasses_avroschema.avrodantic` was removed. To make use of `AvroBaseModel` then
replade the import `from dataclasses_avroschema.avrodantic import AvroBaseModel` by `from dataclasses_avroschema.pydantic import AvroBaseModel`

- If you are using `AvroModel` field attributes like `klass`, `metadata`, etc then all of them now are private (`_klass`, `_metadata`, etc). By design was intended not used them, now
it is explicit.

## Migration from previous versions to 0.45.1

- Previously `Unions` that had `default_factory` where force to return a `callable` which the return type must be `list` or `dict`, now is not the case any more. If you use `default_factory` makes sure that it is a `callable`, that's it. This new fix also will be complain with type checkers.

```python
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class Bus(AvroModel):
    "A Bus"
    engine_name: str

    class Meta:
        namespace = "types"


@dataclasses.dataclass
class Car(AvroModel):
    "A Car"
    engine_name: str

    class Meta:
        namespace = "types"


@dataclasses.dataclass
class UnionSchema(AvroModel):
  "Some Unions"
  lake_trip: Bus | Car
  river_trip: Bus | Car | None = None
  mountain_trip: Bus | Car = dataclasses.field(
      default_factory=lambda: Bus(engine_name="honda"))
  # mountain_trip: Bus | Car = dataclasses.field(default_factory=lambda: {"engine_name": "honda"}) # OLD WAY

UnionSchema.avro_schema()
```

- `Field` internal api updated:
  - `to_avro` was renamed to `default_to_avro` and is an instance method

## Migration from previous versions to 0.27.0

=== "python <= 3.10"

    - `types.Enum` was replaced with `enum.Enum`. You must create your custom enum, example:

    ```python
    import dataclasses
    from dataclasses_avroschema import AvroModel, types


    class UserAdvance(AvroModel):
        name: str
        age: int
        favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"], default="BLUE")  # --> replace with field!!!
    ```

    should be replaced by:

    ```python
    import enum
    import dataclasses
    from dataclasses_avroschema import AvroModel


    class FavoriteColor(enum.Enum):
        BLUE = "BLUE"
        YELLOW = "YELLOW"
        GREEN = "GREEN"


    class UserAdvance:
        name: str
        age: int
        favorite_colors: FavoriteColor = FavoriteColor.BLUE  # --> field updated!!!
    ```

=== "python >= 3.11"

    - `types.Enum` was replaced with `str, enum.Enum`. You must create your custom enum, example:

    ```python
    import dataclasses
    from dataclasses_avroschema import AvroModel, types


    class UserAdvance(AvroModel):
        name: str
        age: int
        favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"], default="BLUE")  # --> replace with field!!!
    ```

    should be replaced by:

    ```python
    import enum
    import dataclasses
    from dataclasses_avroschema import AvroModel


    # New enum!!
    class FavoriteColor(str, enum.Enum):
        BLUE = "BLUE"
        YELLOW = "YELLOW"
        GREEN = "GREEN"


    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        favorite_colors: FavoriteColor = FavoriteColor.BLUE  # --> field updated!!!
    ```

## Migration from previous versions to 0.23.0

1. Now the name for Nested record uses the `class.__name__` instead of ``class.__name__.lower()_record`.

having this schemas:

```python
import typing

from dataclasses_avroschema import AvroModel


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
import dataclasses
import datetime

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class Location(AvroModel):
    latitude: float
    longitude: float

    class Meta:
        namespace = "types.location_type"  # REQUIRED!!!!


@dataclasses.dataclass
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

```py
# Versions < 0.14.0
import dataclasses
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
```

### new version

```py
import dataclasses
import typing
from dataclasses_avroschema import AvroModel, types


@dataclasses.dataclass
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

```py
import dataclasses
import typing

from dataclasses_avroschema import AvroModel


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

@dataclasses.dataclass
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
