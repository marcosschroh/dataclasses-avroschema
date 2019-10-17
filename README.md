# Dataclasses Avro Schema Generator

Generate [Avro](https://avro.apache.org/docs/1.8.2/spec.html) Schemas from a Python class

[![Build Status](https://travis-ci.org/marcosschroh/dataclasses-avroschema.svg?branch=master)](https://travis-ci.org//dataclasses-avroschema)
[![GitHub license](https://img.shields.io/github/license/marcosschroh/dataclasses-avroschema.svg)](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/marcosschroh/dataclasses-avroschema/branch/master/graph/badge.svg)](https://codecov.io/gh/marcosschroh/dataclasses-avroschema)
![python version](https://img.shields.io/badge/python-3.7%2B-yellowgreen)


## Requirements:

python 3.7+

## Installation

```
pip install dataclasses-avroschema
```

## Doocumentaion

https://marcosschroh.github.io/dataclasses-avroschema/

## Usage:

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

## Features:

* [X] Primitive types: int, long, float, boolean, string and null support
* [X] Complex types: enum, array, map, unions and records support
* [x] Logical Types: date, time, datetime, uuid support
* [X] Schema relations (oneToOne, oneToMany)
* [X] Recursive Schemas
