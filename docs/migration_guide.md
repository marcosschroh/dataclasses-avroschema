## Migration from previous versions to 0.14.0

Now all the dataclasses should inheritance from `AvroModel` and not use anymore the `SchemaGenerator`:

```python
# Versions < 0.14.0

import typing

from dataclasses_avroschema import SchemaGenerator, types


class User:
    "An User"
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"])
    country: str = "Argentina"
    address: str = None

SchemaGenerator(User).avro_schema()

# New versions
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

User.avro_schema()
```

Another changes introduced was the way that extra avro attributes are represented, like `namespace`, `aliases` and whether to include `avro documentation`:

```python
class User:
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    def extra_avro_attributes() -> typing.Dict[str, typing.Any]:
        return {
            "namespace": "test.com.ar/user/v1",
            "aliases": ["User", "My favorite User"]
        }

SchemaGenerator(User, include_schema_doc=False).avro_schema()

# Now is perform using a Meta class

class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    class Meta:
        schema_doc = False
        namespace = "test.com.ar/user/v1"
        aliases = ["User", "My favorite User"]
```
