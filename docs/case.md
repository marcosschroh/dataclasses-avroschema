Sometimes we use `avro schemas` with different sources (some written in Scala, some in Python, etc). With the `case`
you can generate your schemas according to your programming language convention:

```python
import typing

from dataclasses_avroschema import AvroModel, case, types


class UserAdvance(AvroModel):
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    has_car: bool = False
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"])
    country: str = "Argentina"
    address: str = None
    md5: types.Fixed = types.Fixed(16)

    class Meta:
        schema_doc = False


UserAdvance.avro_schema(case_type=case.CAPITALCASE)
```

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
            "type": "enum", "name": "Favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]
            }
        },
        {"name": "Country", "type": "string", "default": "Argentina"},
        {"name": "Address", "type": ["null", "string"], "default": null},
        {"name": "Md5", "type": {"type": "fixed", "name": "Md5", "size": 16}}
    ]
}'
```

Available cases:

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
