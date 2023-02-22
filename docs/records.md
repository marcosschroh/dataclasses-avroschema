# Records

Mapped as a Python class. There are some special avro attributes like `aliases`, `namespace` and `doc` (both not required) that can be specified in a record type.

The `doc` attribute can be set via the docstring class. The `aliases` and `namespaces` must be set using `Class Meta`.

## Basic usage

```python
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    class Meta:
        namespace = "test.com.ar/user/v1"
        aliases = ["User", "My favorite User"]

User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "has_pets", "type": "boolean", "default": false},
    {"name": "money", "type": "double", "default": 100.3}
  ],
  "doc": "My User Class",
  "namespace": "test.com.ar/user/v1",
  "aliases": ["User", "My favorite User"]
}'
```

*(This script is complete, it should run "as is")*

## Class Meta

The `class Meta` is used to specify schema attributes that are not represented by the class fields like `namespace`, `aliases` and whether to include the `schema documentation`. Also custom schema name (the default is the class' name) via `schema_name` attribute and `alias_nested_items` when you have nested items and you want to use custom naming for them and `custom dacite` configuration can be provided.

```python title="Class Meta description"
class Meta:
    schema_name = "Name other than the class name"
    schema_doc = False
    namespace = "test.com.ar/user/v1"
    aliases = ["User", "My favorite User"]
    alias_nested_items = {"address": "Address"}
    dacite_config = {
        "strict_unions_match": True,
        "strict": True,
    }
```

`schema_doc (Union[boolean, str])`: Whether include the `schema documentation` generated from `docstrings`. Default `True`. If the value is a `string` if will be used to generate the schema documentation.

`namespace (optional[str])`: Schema namespace. Default `None`

`aliases (optional[List[str]])`: Schema aliases. Default `None`

`alias_nested_items (optional[Dict[str, str]])`: Nested items names

## Record to json and dict

You can get the `json` and `dict` representation of your instance using `to_json` and `to_dict` methods:

```python title="Json and Dict example"
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3


user = User(name="Bond", age=50)

user.to_json()
# >>> '{"name": "Bond", "age": 50, "has_pets": false, "money": 100.3}'

user.to_dict()
# >>> {'name': 'Bond', 'age': 50, 'has_pets': False, 'money': 100.3}
```

*(This script is complete, it should run "as is")*

## Parsing objects

It is possible to create `python instances` from a `dictionary` using the `parse_obj` method. If you are familiar with `pydantic`, this functionality does the same.
Under the hood `dataclasses-avroschema` uses [dacite](https://github.com/konradhalas/dacite) with a default configuration:

```python
"check_types": False,
"forward_references": {
    Model.__name__: Model,
},
```

where `Model` is the model that you have defined in your code

```python title="Usage"
import typing
from dataclasses import dataclass

from dataclasses_avroschema import AvroModel


@dataclass
class Bus(AvroModel):
    driver: str
    total: int

data = {"driver": "Marcos", "total": 10}
bus = Bus.parse_obj(data=data)

print(bus)
# >>>> Bus(driver='Marcos', total=10)
```

*(This script is complete, it should run "as is")*

### Override dacite config

There are some use cases where a custom `dacite` config is needed, so you can provide one using the `dacite_config` in the `class Meta`.

For example using [Strict unions match](https://github.com/konradhalas/dacite#strict-unions-match)

=== "Default dacite configuration"

    ```python
    import typing
    from dataclasses import dataclass

    from dataclasses_avroschema import AvroModel


    @dataclass
    class Car(AvroModel):
        total: int


    @dataclass
    class Bus(AvroModel):
        driver: str
        total: int


    @dataclass
    class Trip(AvroModel):
        transport: typing.Union[Car, Bus]

    data = {"driver": "Marcos", "total": 10}
    bus = Bus.parse_obj(data=data)

    serialized_val = Trip(transport=bus).serialize()

    print(Trip.deserialize(serialized_val, create_instance=False)) 
    # >>> {"transport": {"driver": "Marcos", "total": 10}}
    
    instance = Trip.deserialize(serialized_val)
    print(instance.transport)  # This is a Car but it should be a Bus!!!
    # >>> Car(total=10)
    ```

=== "Custom dacite configuration"

    ```python
    import typing
    from dataclasses import dataclass

    from dataclasses_avroschema import AvroModel


    @dataclass
    class Car(AvroModel):
        total: int


    @dataclass
    class Bus(AvroModel):
        driver: str
        total: int


    @dataclass
    class Trip(AvroModel):
        transport: typing.Union[Car, Bus]

        class Meta:
            dacite_config = {
                "strict_unions_match": True,
                "strict": True,
            }

    data = {"driver": "Marcos", "total": 10}
    bus = Bus.parse_obj(data=data)

    serialized_val = Trip(transport=bus).serialize()
    print(Trip.deserialize(serialized_val, create_instance=False))
    # >>> {"transport": {"driver": "Marcos", "total": 10}}
    
    instance = Trip.deserialize(serialized_val)
    print(instance.transport)  # Is it s Bus and not a Car!!!
    # >>> Bus(driver='Marcos', total=10)

    ```

*(This script is complete, it should run "as is")*

## Validation

Python classes that inheritance from `AvroModel` has a `validate` method. This method `validates` whether the instance data matches
the schema that it represents, for example:

```python title="Validation example"
from dataclasses import dataclass


from dataclasses_avroschema import AvroModel


@dataclass
class User(AvroModel):
    name: str
    age: int
    has_pets: bool
    money: float
    encoded: bytes

# this creates a proper instance
user_instance = User(
    name="a name",
    age=10,
    has_pets=True,
    money=0,
    encoded=b'hi',
)
assert user_instance.validate()

# set 1 to the name attribute and the fastavro validation should fail
# This is possible because in dataclasses there is not restriction,
# but at the moment of using pydantic this will change
user_instance.name = 1
with pytest.raises(ValidationError) as exc:
    assert user_instance.validate()

assert json.loads(str(exc.value)) == ["User.name is <1> of type <class 'int'> expected string"]
```

*(This script is complete, it should run "as is")*

## Nested schema resolution directly from dictionaries

Sometimes you have a `dictionary` and you want to create an instance without creating the nested objects. This library follows
the same approach as `pydantic` with `parse_obj` method. This is also valid for `avrodantic.AvroBaseModel`.

```python
from dataclasses import dataclass
import typing

from dataclasses_avroschema import AvroModel


@dataclass
class Address(AvroModel):
    "An Address"
    street: str
    street_number: int

@dataclass
class User(AvroModel):
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

## Class inheritance

It is possible to have inheritance so you do not have to repeat the same code. You need to be aware that parent classes might have
attributes with default values and that can cause `TypeError: non-default argument` errors.

!!! hint
    With Python 3.10, it is now possible to do it natively with dataclasses.
    Dataclasses 3.10 added the `kw_only` attribute (similar to attrs). It allows you to specify which fields are keyword_only,
    thus will be set at the end of the init, not causing an inheritance problem.

```python
from dataclasses import dataclass

from dataclasses_avroschema import AvroModel


@dataclass
class Parent(AvroModel):
    name: str
    age: int


@dataclass
class Child(Parent):
    has_pets: bool
    money: float
    encoded: bytes


@dataclass
class Child2(Parent, AvroModel):
    has_pets: bool
    money: float
    encoded: bytes

    class Meta:
        schema_doc = False

Child2.avro_schema()

'{
  "type": "record",
  "name": "Child2",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "has_pets", "type": "boolean", "default": false},
    {"name": "money", "type": "double", "default": 100.3},
    {"name": "encoded", "type": "bytes"}
  ]
}'


assert child_schema["fields"] == child_2_schema["fields"]
```

*(This script is complete, it should run "as is")*
