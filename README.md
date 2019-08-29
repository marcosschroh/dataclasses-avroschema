# Dataclasses Avro Schema Generator

Generate [Avro](https://avro.apache.org/docs/1.8.2/spec.html) Schemas from a Python class

## Requirements:

python 3.7+

## Installation

```
pip install dataclasses-avorschema
```

## Usage:

```python
class User:
    "An User"
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
    country: str = "Argentina"
    address: str = None


user_avro_schema = SchemaGenerator(User).avro_schema()

print(user_avro_schema)

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

## TODO:

1. Schema relations
2. Recursive Schemas
3. Support for Avro Logical Types


