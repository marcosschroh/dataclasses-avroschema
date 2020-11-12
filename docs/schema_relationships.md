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
}'
```

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
}'
```

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

## Avoid name colision in multiple relationships

Sometimes we have relationships where a class is related more than once with a particular class,
and the name for the nested schemas must be diferent, otherwise we will generate an invalid `avro schema`.

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


@dataclass
class Trip(AvroModel):
    start_time: datetime
    start_location: Location  # first relationship
    finish_time: datetime
    finish_location: Location  # second relationship
```

In order to avoid name colisions, the nested name is generated in the following way:

1. Get the lower name of the related class
2. Get the field name
3. Is (1) included in (2)?
   then: (2)_record as result
   otherwise: (1)_(2)_record

Example for start_location:

1. Get the lower name of the related class = `location`
2. Get the field name = `start_location`
3. Is `location` included in `start_location`? yes, so the result is `start_location_record`

```python
'{
  "type": "record",
  "name": "Trip",
  "fields": [
    {
      "name": "start_time",
      "type": {
        "type": "long", "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "start_location",
      "type": {
        "type": "record",
        "name": "start_location_record",
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
        "doc": "Location(latitude: float, longitude: float)"
      }
    },
    {
      "name": "finish_time",
      "type": {
        "type": "long", "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "finish_location",
      "type": {
        "type": "record",
        "name": "finish_location_record",
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
        "doc": "Location(latitude: float, longitude: float)"
      }
    }
  ],
  "doc": "Trip(start_time: datetime.datetime, start_location: __main__.Location, finish_time: datetime.datetime, finish_location: __main__.Location)"
}'
```
