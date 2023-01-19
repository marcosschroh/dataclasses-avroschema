# Dataclasses Avro Schema Generator

Generate [Avro](https://avro.apache.org/docs/1.8.2/spec.html) Schemas from a Python class

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fmarcosschroh%2Fdataclasses-avroschema%2Fbadge%3Fref%3Dmaster&style=flat)](https://actions-badge.atrox.dev/marcosschroh/dataclasses-avroschema/goto?ref=master)
[![GitHub license](https://img.shields.io/github/license/marcosschroh/dataclasses-avroschema.svg)](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/marcosschroh/dataclasses-avroschema/branch/master/graph/badge.svg)](https://codecov.io/gh/marcosschroh/dataclasses-avroschema)
![python version](https://img.shields.io/badge/python-3.7%2B-yellowgreen)

## Requirements

`python 3.7+`

## Installation

```bash
pip install dataclasses-avroschema
```

or with `pydantic` funcionalities

```bash
pip install 'dataclasses-avroschema[pydantic]'
```

## Documentation

https://marcosschroh.github.io/dataclasses-avroschema/

## Usage

### Generating the avro schema

```python
from dataclasses import dataclass
import enum

import typing

from dataclasses_avroschema import AvroModel, types


class FavoriteColor(enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


@dataclass
class User(AvroModel):
    "An User"
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: FavoriteColor
    country: str = "Argentina"
    address: str = None

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]

User.avro_schema()

'{
    "type": "record",
    "name": "User",
    "doc": "An User",
    "namespace": "User.v1",
    "aliases": ["user-v1", "super user"],
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "long"},
        {"name": "pets", "type": "array", "items": "string"},
        {"name": "accounts", "type": "map", "values": "long"},
        {"name": "favorite_color", "type": {"type": "enum", "name": "FavoriteColor", "symbols": ["Blue", "Yellow", "Green"]}}
        {"name": "country", "type": "string", "default": "Argentina"},
        {"name": "address", "type": ["null", "string"], "default": null}
    ]
}'

User.avro_schema_to_python()

{
    "type": "record",
    "name": "User",
    "doc": "An User",
    "namespace": "User.v1",
    "aliases": ["user-v1", "super user"],
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "long"},
        {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}},
        {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}},
        {"name": "favorite_colors", "type": {"type": "enum", "name": "FavoriteColor", "symbols": ["BLUE", "YELLOW", "GREEN"]}},
        {"name": "country", "type": "string", "default": "Argentina"},
        {"name": "address", "type": ["null", "string"], "default": None}
    ],
}
```

### Serialization to avro or avro-json and json payload

For serialization is neccesary to use python class/dataclasses instance

```python
from dataclasses import dataclass

import typing

from dataclasses_avroschema import AvroModel


@dataclass
class Address(AvroModel):
    "An Address"
    street: str
    street_number: int


@dataclass
class User(AvroModel):
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.List[Address]

address_data = {
    "street": "test",
    "street_number": 10,
}

# create an Address instance
address = Address(**address_data)

data_user = {
    "name": "john",
    "age": 20,
    "addresses": [address],
}

# create an User instance
user = User(**data_user)

user.serialize()
# >>> b"\x08john(\x02\x08test\x14\x00"

user.serialize(serialization_type="avro-json")
# >>> b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'

# Get the json from the instance
user.to_json()
# >>> '{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'

# Get a python dict
user.to_dict()
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

```

### Deserialization

Deserialization could take place with an instance dataclass or the dataclass itself. Can return the dict representation or a new class instance

```python
import typing
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class Address(AvroModel):
    "An Address"
    street: str
    street_number: int

@dataclasses.dataclass
class User(AvroModel):
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.List[Address]

avro_binary = b"\x08john(\x02\x08test\x14\x00"
avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'

# return a new class instance!!
User.deserialize(avro_binary)
# >>>> User(name='john', age=20, addresses=[Address(street='test', street_number=10)])

# return a python dict
User.deserialize(avro_binary, create_instance=False)
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

# return a new class instance!!
User.deserialize(avro_json_binary, serialization_type="avro-json")
# >>>> User(name='john', age=20, addresses=[Address(street='test', street_number=10)])

# return a python dict
User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False)
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}
```

## Pydantic integration

To add `dataclasses-avroschema` functionality to `pydantic` you only need to replace `BaseModel` by `AvroBaseModel`:

```python
import typing
import enum
import dataclasses

from dataclasses_avroschema.avrodantic import AvroBaseModel

from pydantic import Field


class FavoriteColor(str, enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


@dataclasses.dataclass
class UserAdvance(AvroBaseModel):
    name: str
    age: int
    pets: typing.List[str] = Field(default_factory=lambda: ["dog", "cat"])
    accounts: typing.Dict[str, int] = Field(default_factory=lambda: {"key": 1})
    has_car: bool = False
    favorite_colors: FavoriteColor = FavoriteColor.BLUE
    country: str = "Argentina"
    address: str = None

    class Meta:
        schema_doc = False


# Avro schema
UserAdvance.avro_schema()
'{
    "type": "record",
    "name": "UserAdvance",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "long"},
        {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}, "default": ["dog", "cat"]},
        {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}, "default": {"key": 1}},
        {"name": "has_car", "type": "boolean", "default": false},
        {"name": "favorite_colors", "type": {"type": "enum", "name": "favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}, "default": "BLUE"},
        {"name": "country", "type": "string", "default": "Argentina"},
        {"name": "address", "type": ["null", "string"], "default": null}
    ]
}'

user = UserAdvance(name="bond", age=50)

# pydantic
user.dict()
# >>> {'name': 'bond', 'age': 50, 'pets': ['dog', 'cat'], 'accounts': {'key': 1}, 'has_car': False, 'favorite_colors': <FavoriteColor.BLUE: 'BLUE'>, 'country': 'Argentina', 'address': None}

# pydantic
user.json()
# >>> '{"name": "bond", "age": 50, "pets": ["dog", "cat"], "accounts": {"key": 1}, "has_car": false, "favorite_colors": "BLUE", "country": "Argentina", "address": null}'

# pydantic
user = UserAdvance(name="bond")

# ValidationError: 1 validation error for UserAdvance
# age
# field required (type=value_error.missing)


# dataclasses-avroschema
event = user.serialize()
print(event)
# >>> b'\x08bondd\x04\x06dog\x06cat\x00\x02\x06key\x02\x00\x00\x00\x12Argentina\x00'

UserAdvance.deserialize(data=event)
# >>> UserAdvance(name='bond', age=50, pets=['dog', 'cat'], accounts={'key': 1}, has_car=False, favorite_colors=<FavoriteColor.BLUE: 'BLUE'>, country='Argentina', address=None)
```

## Examples with python streaming drivers (kafka and redis)

Under [examples](https://github.com/marcosschroh/dataclasses-avroschema/tree/master/examples) folder you can find 3 differents kafka examples, one with [aiokafka](https://github.com/aio-libs/aiokafka) (`async`) showing the simplest use case when a `AvroModel` instance is serialized and sent it thorught kafka, and the event is consumed.
The other two examples are `sync` using the [kafka-python](https://github.com/dpkp/kafka-python) driver, where the `avro-json` serialization and `schema evolution` (`FULL` compatibility) is shown.
Also, there are two `redis` examples using `redis streams` with [walrus](https://github.com/coleifer/walrus) and [redisgears-py](https://github.com/RedisGears/redisgears-py)

## Factory and fixtures

[Dataclasses Avro Schema](https://github.com/marcosschroh/dataclasses-avroschema) also includes a `factory` feature, so you can generate `fast` python instances and use them, for example, to test your data streaming pipelines. Instances can be genrated using the `fake` method.

```python
import typing
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class Address(AvroModel):
    "An Address"
    street: str
    street_number: int


@dataclasses.dataclass
class User(AvroModel):
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.List[Address]


Address.fake()
# >>>> Address(street='PxZJILDRgbXyhWrrPWxQ', street_number=2067)

User.fake()
# >>>> User(name='VGSBbOGfSGjkMDnefHIZ', age=8974, addresses=[Address(street='vNpPYgesiHUwwzGcmMiS', street_number=4790)])
```

## Features

* [X] Primitive types: int, long, double, float, boolean, string and null support
* [X] Complex types: enum, array, map, fixed, unions and records support
* [x] Logical Types: date, time (millis and micro), datetime (millis and micro), uuid support
* [X] Schema relations (oneToOne, oneToMany)
* [X] Recursive Schemas
* [X] Generate Avro Schemas from `faust.Record`
* [X] Instance serialization correspondent to `avro schema` generated
* [X] Data deserialization. Return python dict or class instance
* [X] Generate json from python class instance
* [X] Case Schemas
* [X] Generate models from `avsc` files
* [X] Examples of integration with `kafka` drivers: [aiokafka](https://github.com/aio-libs/aiokafka), [kafka-python](https://github.com/dpkp/kafka-python)
* [X] Example of integration  with `redis` drivers: [walrus](https://github.com/coleifer/walrus) and [redisgears-py](https://github.com/RedisGears/redisgears-py)
* [X] Factory instances
* [X] [Pydantic](https://pydantic-docs.helpmanual.io/) integration

## Development

1. Create a `virtualenv`: `python3.7 -m venv venv && source venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Code linting: `./scripts/format`
4. Run tests: `./scripts/test`
