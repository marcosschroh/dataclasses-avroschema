## Schema Relationships

### OneToOne

An User has one Address example:

```python
from dataclasses_avroschema import AvroModel


class Address(AvroModel):
    "An Address"
    street: str
    street_number: int


class User(AvroModel):
    "An User with Address"
    name: str
    age: int
    address: Address

User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "address", "type": {
      "type": "record",
      "name": "Address",
      "fields": [
        {"name": "street","type": "string"},
        {"name": "street_number", "type": "long"}
      ],
      "doc": "An Address"
      }
    }
  ],
  "doc": "An User with Address"
}'
```

*(This script is complete, it should run "as is")*

## OneToOne Recursive Schema Relationship

An User with only one friend :-( :

```python
import typing

from dataclasses_avroschema import AvroModel


class User(AvroModel):
    "User with self reference as friend"
    name: str
    age: int
    friend: typing.Type["User"] = None

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
      "name": "friend",
      "type": ["null", "User"],
      "default": null
    }
  ],
  "doc": "User with self reference as friend"
}'
```

*(This script is complete, it should run "as is")*

## OneToMany Schema Relationship

An User has multiple Address example:

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
    addresses: typing.List[Address]


User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "addresses", "type": {
        "type": "array",
        "items": {
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
}'
```

*(This script is complete, it should run "as is")*

or OneToMany using a Map:

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


User.avro_schema()


'{
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
}'
```

*(This script is complete, it should run "as is")*

## OneToMany Recursive Schema Relationship

An User with multiple friends :-) :

```python
import typing

from dataclasses_avroschema import AvroModel

# Using a List (Avro Array)
class User(AvroModel):
    "User with self reference as friends"
    name: str
    age: int
    friends: typing.List[typing.Type["User"]] = None


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
      "name": "friends",
      "type": {
        "type": "array",
        "items": "User",
        "name": "friend"
      },
      "default": []
    }
  ],
  "doc": "User with self reference as friends"
}'

# Using a Dict (Avro Map)
class User(AvroModel):
  "User with self reference as friends"
  name: str
  age: int
  friends: typing.Dict[str, typing.Type["User"]] = None

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
      "name": "friends",
      "type": {
        "type": "map",
        "values": "User",
        "name": "friend"
      },
      "default": {}
    }
  ],
  "doc": "User with self reference as friends"
}'
```

*(This script is complete, it should run "as is")*

## Avoid name collision in multiple relationships

Sometimes we have relationships where a class is related more than once with a particular class,
and the name for the nested schemas must be different, otherwise we will generate an invalid `avro schema`.
For those cases, you *MUST* define the `namespace`.

For example:

```python
from dataclasses import dataclass
from datetime import datetime
import json

from dataclasses_avroschema import AvroModel


@dataclass
class Location(AvroModel):
    latitude: float
    longitude: float

    class Meta:
        namespace = "types.location_type"

@dataclass
class Trip(AvroModel):
    start_time: datetime
    start_location: Location  # first relationship
    finish_time: datetime
    finish_location: Location  # second relationship


Trip.avro_schema()
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

*(This script is complete, it should run "as is")*

or with `arrays` or `maps`:

```python
class Location(AvroModel):
    latitude: float
    longitude: float

    class Meta:
        namespace = "types.location_type"
        schema_doc = False


class Trip(AvroModel):
    start_location: Location
    finish_location: typing.List[Location]

    class Meta:
        schema_doc = False


Trip.avro_schema()
```

```json
{
  "type": "record",
  "name": "Trip",
  "fields": [
    {
      "name": "start_location",
      "type":
        {
          "type": "record",
          "name": "Location",
          "fields": [
            {
              "name": "latitude",
              "type": "double"
            },
            {
              "name": "longitude",
              "type": "double"
            }
          ],
          "namespace": "types.location_type"
        }
      },
    {
      "name": "finish_location",
      "type": {
        "type": "array",
        "items": "types.location_type.Location",
        "name": "finish_location"
      }
    }
  ]
}'
```

```python
class Location(AvroModel):
    latitude: float
    longitude: float

    class Meta:
        namespace = "types.location_type"
        schema_doc = False


class Trip(AvroModel):
    start_location: Location
    finish_location: typing.Dict[str, Location]

    class Meta:
        schema_doc = False


Trip.avro_schema()
```

```json
{
  "type": "record",
  "name": "Trip",
  "fields": [
    {
      "name": "start_location",
      "type": {
        "type": "record",
        "name": "Location",
        "fields": [
          {
            "name": "latitude",
            "type": "double"
          },
          {
            "name": "longitude",
            "type": "double"
          }
        ],
        "namespace": "types.location_type"
      }
    },
    {
      "name": "finish_location",
      "type": {
        "type": "map",
        "values": "types.location_type.Location",
        "name": "finish_location"
      }
    }
  ]
}'
```

*(This script is complete, it should run "as is")*

If you want, also you can use custom name for nested items (`nested records`, `arrays` or `maps`) using the property `alias_nested_items` in `class Meta`:

```python
from dataclasses_avroschema import AvroModel


class Address(AvroModel):
    "An Address"
    street: str
    street_number: int

class User(AvroModel):
    "An User with Address"
    name: str
    age: int
    address: Address  # default name Address

    class Meta:
        alias_nested_items = {"address": "MySuperAddress"}
```

`User.avro_schema()` will generate:

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
            "name": "address",
            "type": {
                "type": "record",
                "name": "MySuperAddress",  // renamed it using alias_nested_items
                "fields": [
                    {
                        "name": "street",
                        "type": "string"
                    },
                    {
                        "name": "street_number",
                        "type": "long"
                    }
                ],
                "doc": "An Address"
            }
        } 
    ],
    "doc": "An User with Address"
}
```

*(This script is complete, it should run "as is")*
