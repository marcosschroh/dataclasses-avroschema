# Dataclasses Avro Schema Generator

Generate [Avro](https://avro.apache.org/docs/1.8.2/spec.html) Schemas from a Python class

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fmarcosschroh%2Fdataclasses-avroschema%2Fbadge%3Fref%3Dmaster&style=flat)](https://actions-badge.atrox.dev/marcosschroh/dataclasses-avroschema/goto?ref=master)
[![GitHub license](https://img.shields.io/github/license/marcosschroh/dataclasses-avroschema.svg)](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/marcosschroh/dataclasses-avroschema/branch/master/graph/badge.svg)](https://codecov.io/gh/marcosschroh/dataclasses-avroschema)
![python version](https://img.shields.io/badge/python-3.7%2B-yellowgreen)

## Notice of breaking change

As of version **0.19.0**, the default Avro type for Python ints has been changed from `int` to `long` and the default Avro
type for Python floats has been changed from `float` to `double`. Please take care when upgrading.

## Notice of non-breaking schema changes

As of version **0.21.0** the logic used generate schemas for unions has been updated to match the Avro specification. 
Previously a field like `typing.Union[int, str] = 'STRING TYPE'` would generate the union field `["long", "string"]`, which was incorrect - the Avro specification requires the type of a provided default to match the type of the first element in the union array. 
This update was tested under Full compatibility, and while it wasn't a breaking change (changes to defaults generally go through cleanly), it did generate a new schema version.

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
