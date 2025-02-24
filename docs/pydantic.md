# Pydantic Integration

It is possible to use [pydantic](https://docs.pydantic.dev/latest/) with `dataclasses-avroschema` making use of `AvroBaseModel`:

You must use all the `pydantic` features and all `dataclasses-avroschema` functionality will be injected.

!!! note
    With `pydantic` you do not have to use `python dataclasses`

## Avro and Json schemas

```python title="Basic usage"
import typing
import enum
from dataclasses_avroschema.pydantic import AvroBaseModel

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
UserAdvance.model_json_schema()

{
    'required': ['name', 'age'],
    'title': 'UserAdvance',
    'type': 'object'
    'properties': {
        'name': {'title': 'Name', 'type': 'string'},
        'age': {'title': 'Age', 'type': 'integer'},
        'pets': {'items': {'type': 'string'}, 'title': 'Pets', 'type': 'array'},
        'accounts': {'additionalProperties': {'type': 'integer'}, 'title': 'Accounts', 'type': 'object'},
        'has_car': {'default': False, 'title': 'Has Car', 'type': 'boolean'},
        'favorite_colors': {'allOf': [{'$ref': '#/$defs/FavoriteColor'}], 'default': 'BLUE'},
        'country': {'default': 'Argentina', 'title': 'Country', 'type': 'string'},
        'address': {'default': None, 'title': 'Address', 'type': 'string'}
    },
    '$defs': {'FavoriteColor': {'enum': ['BLUE', 'YELLOW', 'GREEN'], 'title': 'FavoriteColor', 'type': 'string'}},
}
```

*(This script is complete, it should run "as is")*

!!! note
    You must use pydantic.Field instead of dataclasses.field

## Avro schemas with pydantic types

Most of `pydantic` types are supported and from them it is possible to generate `avro fields`. Because `pydantic` types are not native `python types`
the end result will contain extra metadata so the end users will have more context at the moment of using the schema. The extra `metadata` is specified
using the key `pydantic-class`.

### Supported fields

| Avro Type    | Pydantic Type |
|--------------|-------------|
| string       | pydantic.FilePath |
| string       | pydantic.DirectoryPath |
| string       | pydantic.EmailStr |
| string       | pydantic.NameEmail |
| string       | pydantic.AnyUrl |
| string       | pydantic.AnyHttpUrl |
| string       | pydantic.HttpUrl |
| string       | pydantic.FileUrl |
| string       | pydantic.PostgresDsn |
| string       | pydantic.CockroachDsn |
| string       | pydantic.AmqpDsn |
| string       | pydantic.RedisDsn |
| string       | pydantic.MongoDsn |
| string       | pydantic.KafkaDsn |
| string       | pydantic.SecretStr |
| string       | pydantic.IPvAnyAddress |
| string       | pydantic.IPvAnyInterface |
| string       | pydantic.IPvAnyNetwork |
| double       | pydantic.NegativeFloat |
| double       | pydantic.PositiveFloat |
| long         | pydantic.NegativeInt |
| long         | pydantic.PositiveIntstr |

| Avro Type    | Logical type | Pydantic Type |
|--------------|--------------|---------------|
| string       | uuid         | pydantic.UUID1 |
| string       | uuid         | pydantic.UUID3 |
| string       | uuid         | pydantic.UUID4 |
| string       | uuid         | pydantic.UUID5 |
| int          | date         | pydantic.PastDate |
| int          | date         | pydantic.FutureDate |
| long         | timestamp-millis | pydantic.PastDatetime |
| long         | timestamp-millis | pydantic.FutureDatetime |
| long         | timestamp-millis | pydantic.AwareDatetime |
| long         | timestamp-millis | pydantic.NaiveDatetime |

```python
import pydantic
from dataclasses_avroschema.pydantic import AvroBaseModel


class Infrastructure(AvroBaseModel):
    email: pydantic.EmailStr
    postgres_dsn: pydantic.PostgresDsn
    cockroach_dsn: pydantic.CockroachDsn
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    mongo_dsn: pydantic.MongoDsn
    kafka_url: pydantic.KafkaDsn
    total_nodes: pydantic.PositiveInt


Infrastructure.avro_schema()

{
    "type": "record",
    "name": "Infrastructure",
    "fields": [
        {"name": "email", "type": {"type": "string", "pydantic-class": "EmailStr"}},
        {"name": "postgres_dsn", "type": {"type": "string", "pydantic-class": "PostgresDsn"}},
        {"name": "cockroach_dsn", "type": {"type": "string", "pydantic-class": "CockroachDsn"}},
        {"name": "amqp_dsn", "type": {"type": "string", "pydantic-class": "AmqpDsn"}},
        {"name": "redis_dsn", "type": {"type": "string", "pydantic-class": "RedisDsn"}},
        {"name": "mongo_dsn", "type": {"type": "string", "pydantic-class": "MongoDsn"}},
        {"name": "kafka_url", "type": {"type": "string", "pydantic-class": "KafkaDsn"}},
        {"name": "total_nodes", "type": {"type": "long", "pydantic-class": "PositiveInt"}}
    ]
}
```

*(This script is complete, it should run "as is")*

!!! note
    The key `pydantic-class` has been added as `metadata` to have more context when using the schema

## Model generation

If is possible to generate [pydantic models](https://marcosschroh.github.io/dataclasses-avroschema/model_generator/#render-pydantic-models) when `pydantic types` have been used. If a field has the matadata key `pydantic-class`
then the proper pydantic types will be used.

Schema example:

```python
from dataclasses_avroschema import ModelGenerator, ModelType

model_generator = ModelGenerator()

schema = {
    "type": "record",
    "name": "Infrastructure",
    "fields": [
        {"name": "email", "type": {"type": "string", "pydantic-class": "EmailStr"}},
        {"name": "kafka_url", "type": {"type": "string", "pydantic-class": "KafkaDsn"}},
        {"name": "total_nodes", "type": {"type": "long", "pydantic-class": "PositiveInt"}},
        {"name": "event_id", "type": {"type": "string", "logicalType": "uuid", "pydantic-class": "UUID1"}},
        {"name": "landing_zone_nodes", "type": {"type": "array", "items": {"type": "long", "pydantic-class": "PositiveInt"}, "name": "landing_zone_node"}},
        {"name": "total_nodes_in_aws", "type": {"type": "long", "pydantic-class": "PositiveInt"}, "default": 10},
        {"name": "optional_kafka_url", "type": ["null", {"type": "string", "pydantic-class": "KafkaDsn"}], "default": None}
    ]
}

result = model_generator.render(schema=schema, model_type=ModelType.AVRODANTIC.value)

with open("models.py", mode="+w") as f:
    f.write(result)
```

and then render the result:

```python
from dataclasses_avroschema.pydantic import AvroBaseModel
import typing
import pydantic


class Infrastructure(AvroBaseModel):
    email: pydantic.EmailStr
    kafka_url: pydantic.KafkaDsn
    total_nodes: pydantic.PositiveInt
    event_id: pydantic.UUID1
    landing_zone_nodes: typing.List[pydantic.PositiveInt]
    total_nodes_in_aws: pydantic.PositiveInt = 10
    optional_kafka_url: typing.Optional[pydantic.KafkaDsn] = None
```

*(This script is complete, it should run "as is")*

!!! note
    In order to render the pydantic types the base class must be `AVRO_BASE_MODEL` or `PYDANTIC_MODEL`

### Mapping `avro fields` to `pydantic types`

|Avro Type  | Metadata                           | Pydantic Type  |
|-----------|------------------------------------|----------------|
| string    | "pydantic-class": "DirectoryPath"  | pydantic.FilePath |
| string    | "pydantic-class": "DirectoryPath"  | pydantic.DirectoryPath |
| string    | "pydantic-class": "EmailStr"       | pydantic.EmailStr |
| string    | "pydantic-class": "NameEmail"      | pydantic.NameEmail |
| string    | "pydantic-class": "AnyUrl"         | pydantic.AnyUrl |
| string    | "pydantic-class": "AnyHttpUrl"     | pydantic.AnyHttpUrl |
| string    | "pydantic-class": "HttpUrl"        | pydantic.HttpUrl |
| string    | "pydantic-class": "FileUrl"        | pydantic.FileUrl |
| string    | "pydantic-class": "PostgresDsn"    | pydantic.PostgresDsn |
| string    | "pydantic-class": "CockroachDsn    | pydantic.CockroachDsn |
| string    | "pydantic-class": "AmqpDsn"        | pydantic.AmqpDsn |
| string    | "pydantic-class": "RedisDsn"       | pydantic.RedisDsn |
| string    | "pydantic-class": "MongoDsn"       | pydantic.MongoDsn |
| string    | "pydantic-class": "KafkaDsn"       | pydantic.KafkaDsn |
| string    | "pydantic-class": "SecretStr"      | pydantic.SecretStr |
| string    | "pydantic-class": "IPvAnyAddress"  | pydantic.IPvAnyAddress |
| string    | "pydantic-class": "IPvAnyInterface"| pydantic.IPvAnyInterface |
| string    | "pydantic-class": "IPvAnyNetwork"  | pydantic.IPvAnyNetwork |
| double    | "pydantic-class": "NegativeFloat"  | pydantic.NegativeFloat |
| double    | "pydantic-class": "PositiveFloat"  | pydantic.PositiveFloat |
| long      | "pydantic-class": "NegativeInt"    | pydantic.NegativeInt |
| long      | "pydantic-class": "PositiveInt"    | pydantic.PositiveInt |

|Avro Type  | Logical Type | Metadata | Pydantic Type                      |
|-----------|--------------|----------|------------------------------------|
| string    |  uuid        | "pydantic-class": "UUID1"    | pydantic.UUID1 |
| string    |  uuid        | "pydantic-class": "UUID3"    | pydantic.UUID3 |
| string    |  uuid        | "pydantic-class": "UUID4"    | pydantic.UUID4 |
| string    |  uuid        | "pydantic-class": "UUID5"    | pydantic.UUID5 |

## Pydantic and dataclasses_avroschema batteries

### To dict, to json and serialization

```python title="getting dict and json"
user = UserAdvance(name="bond", age=50)

# to_json from dataclasses-avroschema is the same that json from pydantic
assert user.to_json(separators=(",",":",)) == user.model_dump_json()

# to_dict from dataclasses-avroschema is the same that dict from pydantic
assert user.to_dict() == user.model_dump()
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

from dataclasses_avroschema.pydantic import AvroBaseModel


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

!!! note
    The method `parse_obj` is defined by `dataclasses_avroschemas` which internally is calling `model_validate` (introduced in pydantic v2)

*(This script is complete, it should run "as is")*

```python title="validate_python usage"
from typing import List

from pydantic import TypeAdapter

from dataclasses_avroschema.pydantic import AvroBaseModel


class User(AvroBaseModel):
    "User with multiple Address"
    name: str
    age: int


data = [{"name": "bond", "age": 50}, {"name": "bond2", "age": 60}]
UserListValidator = TypeAdapter(List[User])
users = UserListValidator.validate_python(data)

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
from dataclasses_avroschema.pydantic import AvroBaseModel


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

!!! note
    All pydantic supported fields can be used with fake

### Excluding fields

Pydantic Fields can be excluded when `dict`, `json` or `copy` methods are called. This meaans that the exclusion is only for [exporting models](https://docs.pydantic.dev/latest/concepts/fields/#exclude) but not excluded in the instance creations, then the `avro serialization` will include all the class attributes.

```python
import typing
from pydantic import Field
from dataclasses_avroschema.pydantic import AvroBaseModel


class User(AvroBaseModel):
    name: str
    age: int
    pets: typing.List[str] = Field(default_factory=lambda: ["dog", "cat"], exclude=True)
    accounts: typing.Dict[str, int] = Field(default_factory=lambda: {"key": 1}, exclude=True)
    has_car: bool = False

user = User(name="bond", age=50, has_car=True)
print(user)
# >>> User(name='bond', age=50, pets=['dog', 'cat'], accounts={'key': 1}, has_car=True)

print(user.model_dump())
# >>> {'name': 'bond', 'age': 50, 'has_car': True} Excludes pets and accounts !!!

event = user.serialize()
assert user == User.deserialize(event)
```

*(This script is complete, it should run "as is")*

## Model Config

With `AvroBaseModel` you can use the same [Model Config](https://docs.pydantic.dev/latest/usage/model_config/) that `pydantic` provides,
for example:

=== "Not use Enum values"
    ```python
    import enum
    from dataclasses_avroschema.pydantic import AvroBaseModel

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
    from dataclasses_avroschema.pydantic import AvroBaseModel
    from pydantic import ConfigDict


    class Color(str, enum.Enum):
        BLUE = "BLUE"
        RED = "RED"


    class Bus(AvroBaseModel):
        model_config = ConfigDict(use_enum_values=True)
        driver: str
        color: Color

    bus =  Bus(driver="bond", color=Color.RED)
    print(busmodel_dump())
    # >>> {'driver': 'bond', 'color': 'RED'}
    ```

## Adding Custom Field-level Attributes

To add `custom field attributes` the `metadata` attribute must be set in `pydantic.Field`. For more info check [adding-custom-field-level-attributes](https://marcosschroh.github.io/dataclasses-avroschema/fields_specification/#adding-custom-field-level-attributes) section for `dataclasses`.

!!! note
    Make sure that `pydantic.Field` is used and *NOT* `dataclasses.field`

### Custom Data Types as Fields

If needed, you can annotate fields with [custom classes](https://docs.pydantic.dev/latest/concepts/types/#customizing-validation-with-getpydanticcoreschema) that define validators.

### Classes with `__get_pydantic_core_schema__`

!!! note
    The conversion mapping of a custom class to its [supported type](./fields_specification.md#avro-field-and-python-types-summary) must be defined in the model's [`json_encoders`](https://docs.pydantic.dev/1.10/usage/exporting_models/#json_encoders) config.

!!! warning
    [Generating models](#Model-generation) from avro schemas that were generated by classes containing Custom Class fields is not supported.

```python
from typing import Any

from dataclasses_avroschema.pydantic import AvroBaseModel

from pydantic import ConfigDict, GetCoreSchemaHandler
from pydantic_core import core_schema


class CustomClass:
    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        def validate(value):
            if isinstance(value, CustomClass):
                return value
            elif not isinstance(value, str):
                raise ValueError(f"Value must be a string or CustomClass - not {type(value)}")

            return cls(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(CustomClass),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: instance.x),
        )

    def __str__(self) -> str:
        return f"{self.value}"


class MyModel(AvroBaseModel):
    model_config = ConfigDict(json_encoders={CustomClass: str}, arbitrary_types_allowed=True)
    my_id: CustomClass


print(MyModel.avro_schema_to_python())
"""
{
  "type": "record",
  "name": "MyModel",
  "fields": [
    {
      "name": "my_id",
      "type": "string"
    }
  ]
}
"""
```

*(This script is complete, it should run "as is")*
