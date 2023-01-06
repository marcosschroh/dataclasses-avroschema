# Case schemas

Sometimes we use `avro schemas` with different sources (some written in Scala, some in Python, etc). With the `case`
you can generate your schemas according to your programming language convention:

```python  title="Example with CAPITALCASE"
import typing
import dataclasses
import enum

from dataclasses_avroschema import AvroModel, case, types


# New enum!!
class FavoriteColor(enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


@dataclasses.dataclass
class UserAdvance(AvroModel):
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: FavoriteColor
    has_car: bool = False
    country: str = "Argentina"
    address: str = None
    md5: types.Fixed = types.Fixed(16)

    class Meta:
        schema_doc = False


UserAdvance.avro_schema(case_type=case.CAPITALCASE)
```

resulting in

```json
{
    "type": "record", 
    "name": "UserAdvance", 
    "fields": [
        {"name": "Name", "type": "string"},
        {"name": "Age", "type": "long"},
        {"name": "Pets", "type": {
            "type": "array", "items": "string", "name": "Pet"
            }
        },
        {"name": "Accounts", "type": {
            "type": "map", "values": "long", "name": "Account"
            }
        },
        {"name": "Has_car", "type": "boolean", "default": false},
        {"name": "Favorite_colors", "type": {
            "type": "enum", "name": "FavoriteColor", "symbols": ["BLUE", "YELLOW", "GREEN"]
            }
        },
        {"name": "Country", "type": "string", "default": "Argentina"},
        {"name": "Address", "type": ["null", "string"], "default": null},
        {"name": "Md5", "type": {"type": "fixed", "name": "Md5", "size": 16}}
    ]
}'
```

*(This script is complete, it should run "as is")*

!!! note
    Cases do not apply to `records` and `enums` names as they are always expressed in `PascalCase`

## Available cases

|Case| Example|
|----|--------|
|camelcase |'foo_bar_baz' # => "fooBarBaz"|
|capitalcase|'foo_bar_baz' # => "Foo_bar_baz"|
|constcase|'FooBarBaz' # => "_FOO_BAR_BAZ"|
|lowercase|'FooBarBaz' # => "foobarbaz"|
|pascalcase|'FooBarBaz' # => "FooBarBaz"|
|pathcase|'foo_bar_baz' # => "foo/bar/baz"|
|snakecase|'FooBarBaz' # => "foo_bar_baz"|
|spinalcase|'FooBarBaz' # => "-foo-bar-baz"|
|trimcase|'FooBarBaz' # => "FooBarBaz"|
|uppercase|'FooBarBaz' # => "FOOBARBAZ|
|alphanumcase|'Foo_123 Bar!' # =>'Foo123Bar'|
