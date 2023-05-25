# Pydantic Integration

It is possible to use [pydantic](https://pydantic-docs.helpmanual.io/) with `dataclasses-avroschema` making use of `AvroBaseModel`:

You must use use all the `pydantic` features and all `dataclasses-avroschema` functionality will be injected.

!!! note
    With `pydantic` you do not have to use `python dataclasses`

## Avro and Json schemas

```python title="Basic usage"
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
        {"name": "favorite_colors", "type": {"type": "enum", "name": "FavoriteColor", "symbols": ["BLUE", "YELLOW", "GREEN"]}, "default": "BLUE"},
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

!!! note
    You must use pydantic.Field instead of dataclasses.field

## Pydantic and dataclasses_avroschema batteries

### To dict, to json and serialization

```python title="getting dict and json"
user = UserAdvance(name="bond", age=50)

# to_json from dataclasses-avroschema is the same that json from pydantic
assert user.to_json() == user.json()

# to_dict from dataclasses-avroschema is the same that dict from pydantic
assert user.to_dict() == user.dict()
```

```python title="serialization"
event = user.serialize()
print(event)
# >>> b'\x08bondd\x04\x06dog\x06cat\x00\x02\x06key\x02\x00\x00\x00\x12Argentina\x00'

UserAdvance.deserialize(data=event)
# >>> UserAdvance(name='bond', age=50, pets=['dog', 'cat'], accounts={'key': 1}, has_car=False, favorite_colors=<FavoriteColor.BLUE: 'BLUE'>, country='Argentina', address=None)
```

### Parsing Objects

```python title="parse_obj usage"
import typing

from dataclasses_avroschema.avrodantic import AvroBaseModel


class Address(AvroBaseModel):
    "An Address"
    street: str
    street_number: int


class User(AvroBaseModel):
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.List[Address]

data_user = {
    "name": "john",
    "age": 20,
    "addresses": [{
        "street": "test",
        "street_number": 10,
        }],
    }

user = User.parse_obj(data=data_user)
assert type(user.addresses[0]) is Address
```

*(This script is complete, it should run "as is")*

```python title="parse_obj_as usage"
from typing import List

from pydantic import parse_obj_as

from dataclasses_avroschema.avrodantic import AvroBaseModel


class User(AvroBaseModel):
    "User with multiple Address"
    name: str
    age: int


data = [{"name": "bond", "age": 50}, {"name": "bond2", "age": 60}]
users = parse_obj_as(List[User], data)

users[0].avro_schema()
# '{"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}], "doc": "User with multiple Address"}'
```

*(This script is complete, it should run "as is")*

### Fake

It is also possible to create `fake` instances with `pydantic` models:

```python
import typing
import datetime
from pydantic import Field
from dataclasses_avroschema.avrodantic import AvroBaseModel


class User(AvroBaseModel):
    name: str
    age: int
    birthday: datetime.date
    pets: typing.List[str] = Field(default_factory=lambda: ["dog", "cat"])
    accounts: typing.Dict[str, int] = Field(default_factory=lambda: {"key": 1})
    has_car: bool = False

print(User.fake())
# >>> User(name='qWTLkqcIVmSBxpWMpFyR', age=2608, birthday=datetime.date(1982, 3, 30), pets=['wqoEXcJRYjcnJmnIvtiI'], accounts={'JueNdHdzIhHIDsjlHJLc': 779}, has_car=True)
```

*(This script is complete, it should run "as is")*

### Excluding fields

Pydantic Fields can be excluded when `dict`, `json` or `copy` methods are called. This meaans that the exclusion is only for [exporting models](https://docs.pydantic.dev/latest/usage/exporting_models/) but not excluded in the instance creations, then the `avro serialization` will include all the class attributes.

```python
import typing
from pydantic import Field
from dataclasses_avroschema.avrodantic import AvroBaseModel


class User(AvroBaseModel):
    name: str
    age: int
    pets: typing.List[str] = Field(default_factory=lambda: ["dog", "cat"], exclude=True)
    accounts: typing.Dict[str, int] = Field(default_factory=lambda: {"key": 1}, exclude=True)
    has_car: bool = False

user = User(name="bond", age=50, has_car=True)
print(user)
# >>> User(name='bond', age=50, pets=['dog', 'cat'], accounts={'key': 1}, has_car=True)

print(user.dict())
# >>> {'name': 'bond', 'age': 50, 'has_car': True} Excludes pets and accounts !!!

event = user.serialize()
assert user == User.deserialize(event)
```

## Model Config

With `AvroBaseModel` you can use the same [Model Config](https://docs.pydantic.dev/latest/usage/model_config/) that `pydantic` provides,
for example:

=== "Not use Enum values"
    ```python
    import enum
    from dataclasses_avroschema.avrodantic import AvroBaseModel

    class Color(str, enum.Enum):
        BLUE = "BLUE"
        RED = "RED"


    class Bus(AvroBaseModel):
        driver: str
        color: Color

    bus =  Bus(driver="bond", color=Color.RED)
    print(bus.dict())
    # >>> {'driver': 'bond', 'color': <Color.RED: 'RED'>}
    ```

=== "Use Enum values"
    ```python
    import enum
    from dataclasses_avroschema.avrodantic import AvroBaseModel

    class Color(str, enum.Enum):
        BLUE = "BLUE"
        RED = "RED"


    class Bus(AvroBaseModel):
        driver: str
        color: Color

        class Config:
            use_enum_values = True

    bus =  Bus(driver="bond", color=Color.RED)
    print(bus.dict())
    # >>> {'driver': 'bond', 'color': 'RED'}
    ```