# Dataclasses Avro Schema Generator

Generate [Avro](https://avro.apache.org/docs/1.8.2/spec.html) Schemas from a Python class

[![Build Status](https://travis-ci.org/marcosschroh/dataclasses-avroschema.svg?branch=master)](https://travis-ci.org//dataclasses-avroschema)
[![GitHub license](https://img.shields.io/github/license/marcosschroh/dataclasses-avroschema.svg)](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/marcosschroh/dataclasses-avroschema/branch/master/graph/badge.svg)](https://codecov.io/gh/marcosschroh/dataclasses-avroschema)
![python version](https://img.shields.io/badge/python-3.7%2B-yellowgreen)

## Requirements

`python 3.7+`

## Installation

```bash
pip install dataclasses-avroschema
```

## Documentation

https://marcosschroh.github.io/dataclasses-avroschema/

## Usage

### Generating the avro schema

```python
from dataclasses import dataclass

import typing

from dataclasses_avroschema import AvroModel, types


@dataclass
class User(AvroModel):
    "An User"
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"])
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
        {"name": "age", "type": "int"},
        {"name": "pets", "type": "array", "items": "string"},
        {"name": "accounts", "type": "map", "values": "int"},
        {"name": "favorite_colors", "type": "enum", "symbols": ["BLUE", "YELLOW", "GREEN"]},
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
        {"name": "age", "type": "int"},
        {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}},
        {"name": "accounts", "type": {"type": "map", "values": "int", "name": "account"}},
        {"name": "favorite_colors", "type": {"type": "enum", "name": "favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}},
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
# python dict >>> {'name': 'john', 'age': 20, 'addresses': [{'street': 'test', 'street_number': 10}]}

```

### Deserialization

Deserialization could take place with an instance dataclass or the dataclass itself. Can return the dict representation or a new class instance

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

## Examples with python streaming drivers (kafka and redis)

Under [examples](https://github.com/marcosschroh/dataclasses-avroschema/tree/master/examples) folder you can find 3 differents kafka examples, one with [aiokafka](https://github.com/aio-libs/aiokafka) (`async`) showing the simplest use case when a `AvroModel` instance is serialized and sent it thorught kafka, and the event is consumed.
The other two examples are `sync` using the [kafka-python](https://github.com/dpkp/kafka-python) driver, where the `avro-json` serialization and `schema evolution` (`FULL` compatibility) is shown.
Also, there are two `redis` examples using `redis streams` with [walrus](https://github.com/coleifer/walrus) and [redisgears-py](https://github.com/RedisGears/redisgears-py)

## Factory and fixtures

[Dataclasses Avro Schema](https://github.com/marcosschroh/dataclasses-avroschema) also includes a `factory` feature, so you can generate `fast` python instances and use them, for example, to test your data streaming pipelines. Instances can be genrated using the `fake` method.

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


Address.fake()
# >>>> Address(street='PxZJILDRgbXyhWrrPWxQ', street_number=2067)

User.fake()
# >>>> User(name='VGSBbOGfSGjkMDnefHIZ', age=8974, addresses=[Address(street='vNpPYgesiHUwwzGcmMiS', street_number=4790)])
```

## Features

* [X] Primitive types: int, long, float, boolean, string and null support
* [X] Complex types: enum, array, map, fixed, unions and records support
* [x] Logical Types: date, time, datetime, uuid support
* [X] Schema relations (oneToOne, oneToMany)
* [X] Recursive Schemas
* [X] Generate Avro Schemas from `faust.Record`
* [X] Instance serialization correspondent to `avro schema` generated
* [X] Data deserialization. Return python dict or class instance
* [X] Generate json from python class instance
* [X] Examples of integration with `kafka` drivers: [aiokafka](https://github.com/aio-libs/aiokafka), [kafka-python](https://github.com/dpkp/kafka-python)
* [X] Example of integration  with `redis` drivers: [walrus](https://github.com/coleifer/walrus) and [redisgears-py](https://github.com/RedisGears/redisgears-py)
* [X] Factory instances

## Development

1. Create a `virtualenv`: `python3.7 -m venv venv && source venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Code linting: `./scripts/lint`
4. Run tests: `./scripts/test`
