# Dataclasses Avro Schema

Generate [avro schemas](https://avro.apache.org/docs/1.8.2/spec.html) from python dataclasses, [Pydantic](https://docs.pydantic.dev/latest/) models and [Faust](https://faust-streaming.github.io/faust/) Records. [Code generation](https://marcosschroh.github.io/dataclasses-avroschema/model_generator/) from avro schemas. [Serialize/Deserialize](https://marcosschroh.github.io/dataclasses-avroschema/serialization/) python instances with avro schemas

[![Tests](https://github.com/marcosschroh/dataclasses-avroschema/actions/workflows/tests.yaml/badge.svg)](https://github.com/marcosschroh/dataclasses-avroschema/actions/workflows/tests.yaml)
[![GitHub license](https://img.shields.io/github/license/marcosschroh/dataclasses-avroschema.svg)](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/marcosschroh/dataclasses-avroschema/branch/master/graph/badge.svg)](https://codecov.io/gh/marcosschroh/dataclasses-avroschema)
![python version](https://img.shields.io/badge/python-3.10%2B-yellowgreen)

## Requirements

`python 3.10+`

## Installation

with `pip` or `poetry`:

`pip install dataclasses-avroschema` or `poetry add dataclasses-avroschema`

### Extras

- [pydantic](https://docs.pydantic.dev/): `pip install 'dataclasses-avroschema[pydantic]'` or `poetry add dataclasses-avroschema --extras "pydantic"`
- [faust-streaming](https://github.com/faust-streaming/faust): `pip install 'dataclasses-avroschema[faust]'` or `poetry add dataclasses-avroschema --extras "faust"`
- [faker](https://github.com/joke2k/faker): `pip install 'dataclasses-avroschema[faker]'` or `poetry add dataclasses-avroschema --extras "faker"`
- [dc-avro](https://marcosschroh.github.io/dc-avro/): `pip install 'dataclasses-avroschema[cli]'` or `poetry add dataclasses-avroschema --with cli`

*Note*: You can install all extra dependencies with `pip install dataclasses-avroschema[faust,pydantic,faker,cli]` or `poetry add dataclasses-avroschema --extras "pydantic faust faker cli"`

## Documentation

https://marcosschroh.github.io/dataclasses-avroschema/

## Usage

### Generating the avro schema

```python
from dataclasses import dataclass
import enum

import typing

from dataclasses_avroschema import AvroModel


class FavoriteColor(str, enum.Enum):
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
    address: typing.Optional[str] = None

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]


print(User.avro_schema())

# {
#    "type": "record",
#    "name": "User",
#    "fields": [
#        {"name": "name", "type": "string"},
#        {"name": "age", "type": "long"},
#        {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}},
#        {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}},
#        {"name": "favorite_colors", "type": {"type": "enum", "name": "FavoriteColor", "symbols": ["BLUE", "YELLOW", "GREEN"]}},
#        {"name": "country", "type": "string", "default": "Argentina"},
#        {"name": "address", "type": ["null", "string"], "default": null}
#    ], 
#    "doc": "An User",
#    "namespace": "User.v1", 
#    "aliases": ["user-v1", "super user"]
# }

assert User.avro_schema_to_python() == {
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

# serialization
assert user.serialize() == b"\x08john(\x02\x08test\x14\x00"

assert user.serialize(
    serialization_type="avro-json"
) == b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'

# # Get the json from the instance
assert user.to_json() == '{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'

# # Get a python dict
assert user.to_dict() == {
    "name": "john", 
    "age": 20, 
    "addresses": [
        {"street": "test", "street_number": 10}
    ]
}
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
assert User.deserialize(avro_binary) == User(
    name='john', 
    age=20,
    addresses=[Address(street='test', street_number=10)]
)

# return a python dict
assert User.deserialize(avro_binary, create_instance=False) == {
    "name": "john",
    "age": 20,
    "addresses": [
        {"street": "test", "street_number": 10}
    ]
}

# return a new class instance!!
assert User.deserialize(avro_json_binary, serialization_type="avro-json") == User(
    name='john',
    age=20,
    addresses=[Address(street='test', street_number=10)]
)

# return a python dict
assert User.deserialize(
    avro_json_binary,
    serialization_type="avro-json",
    create_instance=False
) == {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}
```

## Pydantic integration

To add `dataclasses-avroschema` functionality to `pydantic` you only need to replace `BaseModel` by `AvroBaseModel`:

```python
import typing
import enum

from dataclasses_avroschema.pydantic import AvroBaseModel

from pydantic import Field, ValidationError


class FavoriteColor(str, enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class UserAdvance(AvroBaseModel):
    name: str
    age: int
    pets: typing.List[str] = Field(default_factory=lambda: ["dog", "cat"])
    accounts: typing.Dict[str, int] = Field(default_factory=lambda: {"key": 1})
    has_car: bool = False
    favorite_colors: FavoriteColor = FavoriteColor.BLUE
    country: str = "Argentina"
    address: typing.Optional[str] = None

    class Meta:
        schema_doc = False


assert UserAdvance.avro_schema_to_python() == {
    "type": "record",
    "name": "UserAdvance",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "long"},
        {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}, "default": ["dog", "cat"]},
        {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}, "default": {"key": 1}},
        {"name": "has_car", "type": "boolean", "default": False},{"name": "favorite_colors", "type": {"type": "enum", "name": "FavoriteColor", "symbols": ["BLUE", "YELLOW", "GREEN"]}, "default": "BLUE"},
        {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": None}
    ]
}

print(UserAdvance.json_schema())

# {
#   "$defs": {"FavoriteColor": {"enum": ["BLUE", "YELLOW", "GREEN"], "title": "FavoriteColor", "type": "string"}},
#   "properties": {
#       "name": {"title": "Name", "type": "string"},
#       "age": {"title": "Age", "type": "integer"},
#       "pets": {"items": {"type": "string"}, "title": "Pets", "type": "array"},
#       "accounts": {"additionalProperties": {"type": "integer"}, "title": "Accounts", "type": "object"},
#       "has_car": {"default": false, "title": "Has Car", "type": "boolean"},
#       "favorite_colors": {"allOf": [{"$ref": "#/$defs/FavoriteColor"}], "default": "BLUE"},
#       "country": {"default": "Argentina", "title": "Country", "type": "string"},
#       "address": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Address"}
#   }, 
#   "required": ["name", "age"],
#   "title": "UserAdvance",
#   "type": "object"
# }"""

user = UserAdvance(name="bond", age=50)

# pydantic
assert user.dict() == {
    'name': 'bond',
    'age': 50,
    'pets': ['dog', 'cat'],
    'accounts': {'key': 1},
    'has_car': False,
    'favorite_colors': FavoriteColor.BLUE,
    'country': 'Argentina',
    'address': None
}

# pydantic
print(user.json())

assert user.json() == '{"name":"bond","age":50,"pets":["dog","cat"],"accounts":{"key":1},"has_car":false,"favorite_colors":"BLUE","country":"Argentina","address":null}'

# pydantic
try:
    user = UserAdvance(name="bond")
except ValidationError as exc:
    ...

# dataclasses-avroschema
event = user.serialize()
assert event == b'\x08bondd\x04\x06dog\x06cat\x00\x02\x06key\x02\x00\x00\x00\x12Argentina\x00'

assert UserAdvance.deserialize(data=event) == UserAdvance(
    name='bond',
    age=50, 
    pets=['dog', 'cat'],
    accounts={'key': 1},
    has_car=False, 
    favorite_colors=FavoriteColor.BLUE,
    country='Argentina', 
    address=None
)
```

## Examples with python streaming drivers (kafka and redis)

Under [examples](https://github.com/marcosschroh/dataclasses-avroschema/tree/master/examples) folder you can find 3 differents kafka examples, one with [aiokafka](https://github.com/aio-libs/aiokafka) (`async`) showing the simplest use case when a `AvroModel` instance is serialized and sent it thorught kafka, and the event is consumed.
The other two examples are `sync` using the [kafka-python](https://github.com/dpkp/kafka-python) driver, where the `avro-json` serialization and `schema evolution` (`FULL` compatibility) is shown.
Also, there are two `redis` examples using `redis streams` with [walrus](https://github.com/coleifer/walrus) and [redisgears-py](https://github.com/RedisGears/redisgears-py)

## Factory and fixtures

[Dataclasses Avro Schema](https://github.com/marcosschroh/dataclasses-avroschema) also includes a `factory` feature, so you can generate `fast` python instances and use them, for example, to test your data streaming pipelines. Instances can be generated using the `fake` method.

*Note*: This feature is not enabled by default and requires you have the `faker` extra installed. You may install it with `pip install 'dataclasses-avroschema[faker]'`

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

- [x] Primitive types: int, long, double, float, boolean, string and null support
- [x] Complex types: enum, array, map, fixed, unions and records support
- [x] `typing.Annotated` supported
- [x] `typing.Literal` supported
- [x] Logical Types: date, time (millis and micro), datetime (millis and micro), uuid support
- [x] Schema relations (oneToOne, oneToMany)
- [x] Recursive Schemas
- [x] Generate Avro Schemas from `faust.Record`
- [x] Instance serialization correspondent to `avro schema` generated
- [x] Data deserialization. Return python dict or class instance
- [x] Generate json from python class instance
- [x] Case Schemas
- [x] Generate models from `avsc` files
- [x] Examples of integration with `kafka` drivers: [aiokafka](https://github.com/aio-libs/aiokafka), [kafka-python](https://github.com/dpkp/kafka-python)
- [x] Example of integration  with `redis` drivers: [walrus](https://github.com/coleifer/walrus) and [redisgears-py](https://github.com/RedisGears/redisgears-py)
- [x] Factory instances
- [x] [Pydantic](https://pydantic-docs.helpmanual.io/) integration

## Development

[Poetry](https://python-poetry.org/docs/) is needed to install the dependencies and develope locally

1. Install dependencies: `poetry install --all-extras`
2. Code linting: `./scripts/format`
3. Run tests: `./scripts/test`
4. Tests documentation: `./scripts/test-documentation`

For commit messages we use [commitizen](https://commitizen-tools.github.io/commitizen/) in order to standardize a way of committing rules
