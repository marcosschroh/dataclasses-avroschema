# Dataclasses Avro Schema Generator

Generate [Avro](https://avro.apache.org/docs/1.8.2/spec.html) Schemas from a Python class

[![Build Status](https://travis-ci.org/marcosschroh/dataclasses-avroschema.svg?branch=master)](https://travis-ci.org//dataclasses-avroschema)
[![GitHub license](https://img.shields.io/github/license/marcosschroh/dataclasses-avroschema.svg)](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/marcosschroh/dataclasses-avroschema/branch/master/graph/badge.svg)](https://codecov.io/gh/marcosschroh/dataclasses-avroschema)
![python version](https://img.shields.io/badge/python-3.7%2B-yellowgreen)

## Requirements

python 3.7+

## Installation

```bash
pip install dataclasses-avroschema
```

## Documentation

https://marcosschroh.github.io/dataclasses-avroschema/

## Usage

```python
from dataclasses_avroschema.schema_generator import SchemaGenerator


class User:
    "An User"
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
    country: str = "Argentina"
    address: str = None

SchemaGenerator(User).avro_schema()

'{
    "type": "record",
    "name": "User",
    "doc": "An User",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"},
        {"name": "pets", "type": "array", "items": "string"},
        {"name": "accounts", "type": "map", "values": "int"},
        {"name": "favorite_colors", "type": "enum", "symbols": ["BLUE", "YELLOW", "GREEN"]},
        {"name": "country", "type": ["string", "null"], "default": "Argentina"},
        {"name": "address", "type": ["null", "string"], "default": "null"}
    ]
}'
```

and serialization

```python
import typing

from dataclasses_avroschema.schema_generator import SchemaGenerator


@dataclass
class Address:
    "An Address"
    street: str
    street_number: int

@dataclass
class User:
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
schema = SchemaGenerator(user)

schema.serialize()
# >>> b"\x08john(\x02\x08test\x14\x00"

schema.serialize(serialization_type="avro-json")
# >>> b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'
```

## Features

* [X] Primitive types: int, long, float, boolean, string and null support
* [X] Complex types: enum, array, map, fixed, unions and records support
* [x] Logical Types: date, time, datetime, uuid support
* [X] Schema relations (oneToOne, oneToMany)
* [X] Recursive Schemas
* [X] Generate Avro Schemas from `faust.Record`
* [X] Instance serialization correspondent to `avro schema` generated
* [X] Data deserialization

## Development

1. Create a `virtualenv`: `python3.7 -m venv venv && source venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Code linting: `./scripts/lint`
4. Run tests: `./scripts/test`
