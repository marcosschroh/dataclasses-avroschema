It is possible to use [pydantic](https://pydantic-docs.helpmanual.io/) with `dataclasses-avroschema` making use of `AvroBaseModel`:

You must use use all the `pydantic` features and all `dataclasses-avroschema` functionality will be injected. 

## Avro and Json schemas

```python
import typing
import enum
from dataclasses_avroschema.avrodantic import AvroBaseModel

from pydantic import Field


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

# Json schema
UserAdvance.json_schema()

'{
    "title": "UserAdvance",
    "type": "object",
    "properties": {
        "name": {"title": "Name", "type": "string"},
        "age": {"title": "Age", "type": "integer"},
        "pets": {"title": "Pets", "type": "array", "items": {"type": "string"}},
        "accounts": {"title": "Accounts", "type": "object", "additionalProperties": {"type": "integer"}},
        "has_car": {"title": "Has Car", "default": false, "type": "boolean"},
        "favorite_colors": {"default": "BLUE", "allOf": [{"$ref": "#/definitions/FavoriteColor"}]},
        "country": {"title": "Country", "default": "Argentina", "type": "string"},
        "address": {"title": "Address", "type": "string"}},
        "required": ["name", "age"], "definitions": {"FavoriteColor": {"title": "FavoriteColor", "description": "An enumeration.", "enum": ["BLUE", "YELLOW", "GREEN"], "type": "string"}}}'
```
*(This script is complete, it should run "as is")*

## To dict and json

```python
user = UserAdvance(name="bond", age=50)

# to_json from dataclasses-avroschema is the same that json from pydantic
assert user.to_json() == user.json()

# to_dict from dataclasses-avroschema is the same that dict from pydantic
assert user.to_dict() == user.dict()
```

## Serialization

```python
event = user.serialize()
print(event)
# >>> b'\x08bondd\x04\x06dog\x06cat\x00\x02\x06key\x02\x00\x00\x00\x12Argentina\x00'

UserAdvance.deserialize(data=event)
# >>> UserAdvance(name='bond', age=50, pets=['dog', 'cat'], accounts={'key': 1}, has_car=False, favorite_colors=<FavoriteColor.BLUE: 'BLUE'>, country='Argentina', address=None)
```
