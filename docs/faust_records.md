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

## Faust and dataclasses_avroschema batteries

### To dict, to json and serialization

```python
import typing

from faust.models import fields

from dataclasses_avroschema.faust import AvroRecord


class Address(AvroRecord):
    street: str
    street_number: int


class UserAdvance(AvroRecord):
    name: str
    age: int
    address: Address
    pets: typing.List[str] = fields.StringField(required=False, default=['dog', 'cat'])
    accounts: typing.Dict[str, int] = fields.IntegerField(required=False, default={"key": 1})
    has_car: bool = fields.BooleanField(required=False, default=False)
    favorite_colors: typing.Tuple[str] = fields.StringField(required=False, default=("BLUE", "YELLOW", "GREEN"))
    country: str = fields.StringField(required=False, default="Argentina")

    class Meta:
        schema_doc = False


user = UserAdvance(
    name="bond",
    age=50, 
    address=Address(
        street="Wilhelminastraat",
        street_number=29,
    )
)


assert user.to_dict() == {
    'name': 'bond', 'age': 50, 
    'address': {
        'street': 'Wilhelminastraat', 
        'street_number': 29
    }, 
    'pets': ['dog', 'cat'], 
    'accounts': {'key': 1},
    'has_car': False,
    'favorite_colors': ('BLUE', 'YELLOW', 'GREEN'), 
    'country': 'Argentina'
}

assert user.to_json(separators=(",",":",)) == """{"name":"bond","age":50,"address":{"street":"Wilhelminastraat","street_number":29},"pets":["dog","cat"],"accounts":{"key":1},"has_car":false,"favorite_colors":["BLUE","YELLOW","GREEN"],"country":"Argentina"}"""

event = user.serialize()
assert event == b'\x08bondd Wilhelminastraat:\x04\x06dog\x06cat\x00\x02\x06key\x02\x00\x00\x06\x08BLUE\x0cYELLOW\nGREEN\x00\x12Argentina'

assert UserAdvance.deserialize(data=event) == UserAdvance(name='bond', age=50, address=Address(street='Wilhelminastraat', street_number=29), pets=['dog', 'cat'], accounts={'key': 1}, has_car=False, favorite_colors=('BLUE', 'YELLOW', 'GREEN'), country='Argentina')
```
