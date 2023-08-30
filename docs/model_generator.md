# Model Generator

This section describe how to convert `python classes` from an `avro schema` (avsc files). This is the inverse process that the library aims to.

**`Avro schema` --> `Python class`**

In order to create the models, we should use the `ModelGenerator` class. This class will be in charge of render all the python types in a proper way.
The rendered result is a string that contains the proper identation, so the result can be saved in a file and it will be ready to use.

!!! note
    In future releases it will be possible to generate models for other programming langagues like `java` and `rust`

!!! note
    You can also use [dc-avro](https://github.com/marcosschroh/dc-avro) to generate the models from the command line

## Mapping `avro fields` to `python fields` summary

|Avro Type | Python Type  |
|-----------|-------------|
| string    | str         |
| int       | long        |
| boolean   | bool        |
| float     | double      |
| null      | None        |
| bytes     | bytes       |
| array     | typing.List |
| map       | typing.Dict |
| fixed     | types.confixed |
| enum      | enum.Enum   |
| int       | types.Int32 |
| float     | types.Float32|
| union     | typing.Union|
| record    | Python class|
| date      | datetime.date|
| time-millis| datetime.time|
| time-micros| types.TimeMicro|
| timestamp-millis| datetime.datetime|
| timestamp-micros| types.DateTimeMicro|
| decimal | types.condecimal|
| uuid | uuid.UUID    |

## Usage

```python
from dataclasses_avroschema import ModelGenerator

model_generator = ModelGenerator()

schema = {
    "type": "record",
    "namespace": "com.kubertenes",
    "name": "AvroDeployment",
    "fields": [
        {"name": "image", "type": "string"},
        {"name": "replicas", "type": "int"},
        {"name": "port", "type": "int"},
    ],
}

result = model_generator.render(schema=schema)

# save the result in a file
with open("models.py", mode="+w") as f:
    f.write(result)
```

Then, the end result is:

```python
# models.py
import dataclasses

from dataclasses_avroschema import AvroModel
from dataclasses_avroschema import types


@dataclasses.dataclass
class AvroDeployment(AvroModel):
    image: str
    replicas: types.Int32
    port: types.Int32

    class Meta:
        namespace = "com.kubertenes"
```

## Render a Python module

It's also possible to generate a Python module containing classes from multiple schemas using `render_module`.

```py
from dataclasses_avroschema import ModelGenerator

model_generator = ModelGenerator()

user_schema = {
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "name", "type": "string", "default": "marcos"},
        {"name": "age", "type": "int"},
    ],
}
address_schema = {
    "type": "record",
    "name": "Address",
    "fields": [
        {"name": "street", "type": "string"},
        {"name": "street_number", "type": "long"},
    ],
}

result = model_generator.render_module(schemas=[user_schema, address_schema])

with open("models.py", mode="+w") as f:
    f.write(result)
```

Then, the end result is:

```py
# models.py
from dataclasses_avroschema import AvroModel
from dataclasses_avroschema import types
import dataclasses


@dataclasses.dataclass
class User(AvroModel):
    age: types.Int32
    name: str = "marcos"


@dataclasses.dataclass
class Address(AvroModel):
    street: str
    street_number: int
```

Generating a single module from multiple schemas is useful for example to group schemas that belong to the same namespace.

## Render Pydantic models

It is also possible to render `BaseModel` (pydantic) and `AvroBaseModel` (avro + pydantic) models as well simply specifying the `base class`.
The end result will also include the necessaty imports and the use of `pydantic.Field` in case that it is needed:

For example:

```python
schema = {
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "long"},
        {"name": "friend", "type": ["null", "User"], "default": None},
        {"name": "relatives", "type": {"type": "array", "items": "User", "name": "relative"}, "default": []},
        {"name": "teammates", "type": {"type": "map", "values": "User", "name": "teammate"}, "default": {}},
        {"name": "money", "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 3}},
    ],
}
```

and then render the result:

=== "Pydantic models"

    ```python
    from dataclasses_avroschema import ModelGenerator, BaseClassEnum

    model_generator = ModelGenerator(base_class=BaseClassEnum.PYDANTIC_MODEL.value)
    result = model_generator.render(schema=schema)

    # save the result in a file
    with open("models.py", mode="+w") as f:
        f.write(result)

    # models.py
    from pydantic import BaseModel
    from pydantic import Field
    from pydantic import condecimal
    import typing


    class User(BaseModel):
        name: str
        age: int
        money: condecimal(max_digits=10, decimal_places=3)
        friend: typing.Optional[typing.Type["User"]] = None
        relatives: typing.List[typing.Type["User"]] = Field(default_factory=list)
        teammates: typing.Dict[str, typing.Type["User"]] = Field(default_factory=dict)
    ```

=== "Avrodantic models"

    ```python
    from dataclasses_avroschema import ModelGenerator, BaseClassEnum

    model_generator = ModelGenerator(base_class=BaseClassEnum.AVRO_DANTIC_MODEL.value)
    result = model_generator.render(schema=schema)

    # save the result in a file
    with open("models.py", mode="+w") as f:
        f.write(result)

    # models.py
    from dataclasses_avroschema.avrodantic import AvroBaseModel
    from pydantic import Field
    from pydantic import condecimal
    import typing


    class User(AvroBaseModel):
        name: str
        age: int
        money: condecimal(max_digits=10, decimal_places=3)
        friend: typing.Optional[typing.Type["User"]] = None
        relatives: typing.List[typing.Type["User"]] = Field(default_factory=list)
        teammates: typing.Dict[str, typing.Type["User"]] = Field(default_factory=dict)
    ```

!!! note
    Use the `dataclasses_avroschema.BaseClassEnum` to specify the `base class`

!!! note
    `decimal.Decimal` are created using `pydantic condecimal`

!!! note
    `uuid` types are created using `pydantic.UUID4`

## Malformed schemas

Some times there are valid avro schemas but we could say that it is "malformed", for example the following schema has a field name called `Address` which is
exactly the same name as the record `Address`.

```python
{
  "type": "record",
  "name": "User",
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
      "name": "Address",  # The field name is the same as the record name
      "type": [
        "null",
        {
            "type": "record",
            "name": "Address",
            "fields": [
            {
                "name": "name",
                "type": "string"
            }
            ]
        },
      ],
      "default": None,
    }
  ]
}
```

If we try to generate the python models that correspond with the previous schema we end up with the following result:

```python
from dataclasses_avroschema import AvroModel
import dataclasses
import typing


@dataclasses.dataclass
class Address(AvroModel):
    name: str


@dataclasses.dataclass
class User(AvroModel):
    name: str
    age: int
    Address: typing.Optional[Address] = None
```

The result is correct because it translate to python what the schema represents, but if we checked the `annotations` we see that `Address` is `overshadowed`:

```python
print(User.__annotations__)
# >>> {'name': str, 'age': int, 'Address': NoneType}

# We do not want this!!!
print(User.fake())
# >>> User(name='ftXgdDSUzdUIamiiHOiS', age=2422, Address=None)  
```

If we rename the field name `Address` to `address` in the schema:

```python
{
  "type": "record",
  "name": "User",
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
      "name": "address",  # RENAMED!!!
      "type": [
        "null",
        {
            "type": "record",
            "name": "Address",
            "fields": [
            {
                "name": "name",
                "type": "string"
            }
            ]
        },
      ],
      "default": None,
    }
  ]
}
```

we get a proper result:

```python
from dataclasses_avroschema import AvroModel
import dataclasses
import typing


@dataclasses.dataclass
class Address(AvroModel):
    name: str


@dataclasses.dataclass
class User(AvroModel):
    name: str
    age: int
    address: typing.Optional[Address] = None

print(User.__annotations__)
# >>> {'name': str, 'age': int, 'address': typing.Optional[__main__.Address]}

print(User.fake())
# >>> User(name='JBZdhEWdXwFLQitWCjkc', age=3406, address=Address(name='AhlQsvXnkpcPZJvRSXLr'))
```

## Field order

Sometimes we have to work with schemas that were created by a third party and we do not have control over them. Those schemas can contain optional fields
declared before required fields, which means that and invalid model will be generated. To avoid this problem the `field_order` property is used in the generation process.
For example the following schema contains the field `has_pets` (optional) before required fields:

```python
from dataclasses_avroschema import ModelGenerator


schema = {
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "has_pets", "type": "boolean", "default": False},
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "money", "type": "double", "default": 100.3}
  ],
  "doc": "My User Class",
}

model_generator = ModelGenerator()
result = model_generator.render(schema=schema)

# save the result in a file
with open("models.py", mode="+w") as f:
    f.write(result)
```

Then the result will be:

```python
# models.py
from dataclasses_avroschema import AvroModel
import dataclasses


@dataclasses.dataclass
class User(AvroModel):
    """
    My User Class
    """
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    class Meta:
        field_order = ['has_pets', 'name', 'age', 'money']
```

## Enums and case sensitivity

Sometimes there are schemas that contains the `symbols` which are case sensivity, for example `"symbols": ["P", "p"]`.
Having something like that is NOT reccomended at all because it is meaninless, really hard to undestand the intention of it. Avoid it!!!

When the schema generator encounter this situation it can not generated the proper `enum` with `uppercases` key so it will use the `symbol` without any transformation

```python
from dataclasses_avroschema import ModelGenerator

schema = {
    "type": "record",
    "name": "User",
    "fields": [
        {
            "name": "unit_multi_player",
            "type": {
                "type": "enum",
                "name": "unit_multi_player",
                "symbols": ["Q", "q"],
            },
        }
    ],
}

model_generator = ModelGenerator()
result = model_generator.render(schema=schema)

# save the result in a file
with open("models.py", mode="+w") as f:
    f.write(result)
```

Then the result will be:

```python
# models.py
from dataclasses_avroschema import AvroModel
import dataclasses
import enum


class UnitMultiPlayer(enum.Enum):
    Q = "Q"
    q = "q"


@dataclasses.dataclass
class User(AvroModel):
    unit_multi_player: UnitMultiPlayer

```

As the example shows the second enum member `UnitMultiPlayer.p` is not in uppercase otherwise will collide with the first member `UnitMultiPlayer.P`
