# Faust integration

This library also has support to generate `Avro Schemas` from a `faust.Record` using `AvroRecord`.
`AvroRecord` is just a class that inherits from `faust.Record` and `AvroModel` respectively.

!!! note
    All the AvroModel features like `serialization`, `parsing objects`, `validation` and `fake`, are available with AvroRecord

Example:

```python title="Basic usage"
import typing
from faust.models import fields
from dataclasses_avroschema.faust import AvroRecord


class UserAdvance(AvroRecord):
    name: str
    age: int
    pets: typing.List[str] = fields.StringField(required=False, default=["dog", "cat"])
    accounts: typing.Dict[str, int] = fields.IntegerField(required=False, default={"key": 1})
    has_car: bool = fields.BooleanField(required=False, default=False)
    favorite_colors: typing.Tuple[str] = fields.StringField(required=False, default=("BLUE", "YELLOW", "GREEN"))
    country: str = fields.StringField(required=False, default="Argentina")
    address: typing.Optional[str] = None

    class Meta:
        schema_doc = False


UserAdvance.avro_schema()
```

resulting in

```json
{
  "type": "record",
  "name": "UserAdvance",
  "fields": [
    {
      "name": "name",
      "type": "string"
    },
    {
      "name": "age",
      "type": "long"
    },
    {
      "name": "pets",
      "type": {
        "type": "array",
        "items": "string",
        "name": "pet"
      },
      "default": ["dog", "cat"]
    },
    {
      "name": "accounts",
      "type": {
        "type": "map",
        "values": "long",
        "name": "account"
      },
      "default": {"key": 1}
    },
    {
      "name": "has_car",
      "type": "boolean",
      "default": false
    },
    {
      "name": "favorite_colors", 
      "type": {
        "type": "array", "items": "string", "name": "favorite_color",
        "default": ["BLUE", "YELLOW", "GREEN"]
      }
    },
    {
      "name": "country",
      "type": "string",
      "default": "Argentina"
    },
    {
      "name": "address",
      "type": ["null", "string"],
      "default": null
    }
  ]
}
```

*(This script is complete, it should run "as is")*

## Data validation

For models there is no validation of data by default in `Faust`, however there is an option that will enable validation for all common JSON fields (int, float, str, etc.), and some commonly used Python ones (datetime, Decimal, etc.)

In order to validate the data `validation=True` must be used as is described in tha [faust documenation](https://faust-streaming.github.io/faust/userguide/models.html#validation)

=== "Data validation"

    ```python title="Data validation"
    import typing
    from faust.models import fields
    from dataclasses_avroschema.faust import AvroRecord


    class UserAdvance(AvroRecord, validation=True):
        name: str
        age: int
        pets: typing.List[str] = fields.StringField(required=False, default=['dog', 'cat'])
        accounts: typing.Dict[str, int] = fields.IntegerField(required=False, default={"key": 1})
        has_car: bool = fields.BooleanField(required=False, default=False)
        favorite_colors: typing.Tuple[str] = fields.StringField(required=False, default=("BLUE", "YELLOW", "GREEN"))
        country: str = fields.StringField(required=False, default="Argentina")
        address: typing.Optional[str] = None

        class Meta:
            schema_doc = False

    UserAdvance(name="marcos", age="bond")

    ValueError: invalid literal for int() with base 10: 'bond'
    ```

=== "No Data validation"
    ```python
    import typing

    from dataclasses_avroschema.faust import AvroRecord


    class UserAdvance(AvroRecord):
        name: str
        age: int
        pets: typing.List[str] = fields.StringField(required=False, default=['dog', 'cat'])
        accounts: typing.Dict[str, int] = fields.IntegerField(required=False, default={"key": 1})
        has_car: bool = fields.BooleanField(required=False, default=False)
        favorite_colors: typing.Tuple[str] = fields.StringField(required=False, default=("BLUE", "YELLOW", "GREEN"))
        country: str = fields.StringField(required=False, default="Argentina")
        address: typing.Optional[str] = None

        class Meta:
            schema_doc = False

    UserAdvance(name="marcos", age="juan")  # WRONG data
    ```

*(This script is complete, it should run "as is")*
