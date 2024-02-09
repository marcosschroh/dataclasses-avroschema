# Dataclasses Avro Schema Generator

Generate [Avro](https://avro.apache.org/docs/1.8.2/spec.html) Schemas from a Python class

[![Tests](https://github.com/marcosschroh/dataclasses-avroschema/actions/workflows/tests.yaml/badge.svg)](https://github.com/marcosschroh/dataclasses-avroschema/actions/workflows/tests.yaml)
[![GitHub license](https://img.shields.io/github/license/marcosschroh/dataclasses-avroschema.svg)](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/marcosschroh/dataclasses-avroschema/branch/master/graph/badge.svg)](https://codecov.io/gh/marcosschroh/dataclasses-avroschema)
![python version](https://img.shields.io/badge/python-3.8%2B-yellowgreen)

## Requirements

`python 3.8+`

## Installation

with `pip` or `poetry`:

`pip install dataclasses-avroschema` or `poetry install dataclasses-avroschema`

### Extras

- [pydantic](https://docs.pydantic.dev/): `pip install 'dataclasses-avroschema[pydantic]'` or `poetry install dataclasses-avroschema --extras "pydantic"`
- [faust-streaming](https://github.com/faust-streaming/faust): `pip install 'dataclasses-avroschema[faust]'` or `poetry install dataclasses-avroschema --extras "faust "`
- [faker](https://github.com/joke2k/faker): `pip install 'dataclasses-avroschema[faker]'` or `poetry install dataclasses-avroschema --extras "faker"`

*Note*: You can install all extra dependencies with `pip install dataclasses-avroschema[faust, pydantic, faker]` or `poetry install dataclasses-avroschema --extras "pydantic faust faker"`

### CLI

To install `avro schemas cli` install [dc-avro](https://marcosschroh.github.io/dc-avro/)

`pip install 'dataclasses-avroschema[cli]'` or `poetry install dataclasses-avroschema --with cli`

## Usage

### Generating the avro schema

```python title="Trival Usage"
import enum
import typing
import dataclasses

from dataclasses_avroschema import AvroModel


class FavoriteColor(enum.Enum):
    BLUE = "Blue"
    YELLOW = "Yellow"
    GREEN = "Green"


@dataclasses.dataclass
class User(AvroModel):
    "An User"
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_color: FavoriteColor
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
        {"name": "favorite_color", "type": {"type": "enum", "name": "FavoriteColor", "symbols": ["BLUE", "YELLOW", "GREEN"]}},
        {"name": "country", "type": "string", "default": "Argentina"},
        {"name": "address", "type": ["null", "string"], "default": None}
    ],
}
```
