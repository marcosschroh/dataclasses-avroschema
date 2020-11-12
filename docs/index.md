# Dataclasses Avro Schema Generator

Generate [Avro](https://avro.apache.org/docs/1.8.2/spec.html) Schemas from a Python class

[![Build Status](https://travis-ci.org/marcosschroh/dataclasses-avroschema.svg?branch=master)](https://travis-ci.org//dataclasses-avroschema)
[![GitHub license](https://img.shields.io/github/license/marcosschroh/dataclasses-avroschema.svg)](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/marcosschroh/dataclasses-avroschema/branch/master/graph/badge.svg)](https://codecov.io/gh/marcosschroh/dataclasses-avroschema)
![python version](https://img.shields.io/badge/python-3.7%2B-yellowgreen)

## Notice of breaking change

As of version **0.19.0**, the default Avro type for Python ints has been changed from `int` to `long` and the default Avro
type for Python floats has been changed from `float` to `double`. Please take care when upgrading.

## Requirements

`python 3.7+`

## Installation

```bash
pip install dataclasses-avroschema
```

## Usage

### Generating the avro schema

```python
import typing

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
        {"name": "age", "type": "long"},
        {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}},
        {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}},
        {"name": "favorite_colors", "type": {"type": "enum", "name": "favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}},
        {"name": "country", "type": "string", "default": "Argentina"},
        {"name": "address", "type": ["null", "string"], "default": None}
    ],
}
```
