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
    {"name": "age", "type": "int"},
    {"name": "address", "type": {
      "type": "record",
      "name": "Address",
      "fields": [
        {"name": "street","type": "string"},
        {"name": "street_number", "type": "int"}
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
      "type": "int"
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
    {"name": "age", "type": "int"},
    {"name": "addresses", "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "Address",
          "fields": [
            {"name": "street", "type": "string"},
            {"name": "street_number", "type": "int"}
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
    {"name": "age", "type": "int"},
    {"name": "addresses", "type": {
        "type": "map",
        "values": {
          "type": "record",
          "name": "Address",
          "fields": [
            {"name": "street", "type": "string"},
            {"name": "street_number", "type": "int"}
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
      "type": "int"
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
      "type": "int"
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
