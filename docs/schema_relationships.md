## OneToOne Schema relationship

An User has one Address example:

```python
from dataclasses_avroschema.schema_generator import SchemaGenerator


class Address:
    "An Address"
    street: str
    street_number: int


class User:
    "An User with Address"
    name: str
    age: int
    address: Address

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
      "name": "address",
      "type": {
        "type": "record",
        "name": "Address",
        "fields": [
          {
            "name": "street",
            "type": "string"
          },
          {
            "name": "street_number",
            "type": "int"
          }
        ],
        "doc": "An Address"
      }
    }
  ],
  "doc": "An User with Address"
}'
```

## OneToMany Schema relationshop 

An User has multiple Address example:

```python
import typing

from dataclasses_avroschema.schema_generator import SchemaGenerator


class Address:
    "An Address"
    street: str
    street_number: int


class User:
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.List[Address]


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
      "name": "addresses",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "Address",
          "fields": [
            {
              "name": "street",
              "type": "string"
            },
            {
              "name": "street_number",
              "type": "int"
            }
          ],
          "doc": "An Address"
        },
        "name": "addresses"
      }
    }
   ],
   "doc": "User with multiple Address"
}'
```

or OneToMany using a Map:

```python
import typing

from dataclasses_avroschema.schema_generator import SchemaGenerator


class Address:
    "An Address"
    street: str
    street_number: int


class User:
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.Dict[str, Address]


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
      "name": "addresses",
      "type": {
        "type": "map",
        "values": {
          "type": "record",
          "name": "Address",
          "fields": [
            {
              "name": "street",
              "type": "string"
            },
            {
              "name": "street_number",
              "type": "int"
            }
          ],
          "doc": "An Address"
        },
        "name": "addresses"
      }
    }
  ],
  "doc": "User with multiple Address"
}'
```