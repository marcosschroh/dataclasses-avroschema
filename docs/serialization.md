# Serialization

Is possible to `serialize/deserialize` with the correspondent avro schema generated and the dataclass.
In both cases we can do it with `avro` or `avro-json`.

## Instances serialization

```python title="Avro and avro-json serialization"
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

address_data = {
    "street": "test",
    "street_number": 10,
}

# create an Address instance
address = Address(**address_data)

data_user = {
    "name": "john",
    "age": 20,
    "addresses": [address],
}

# create an User instance
user = User(**data_user)

user.serialize()
# >>> b"\x08john(\x02\x08test\x14\x00"

user.serialize(serialization_type="avro-json")
# >>> b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'

user.to_json()
# python dict >>> {'name': 'john', 'age': 20, 'addresses': [{'street': 'test', 'street_number': 10}]}
```

*(This script is complete, it should run "as is")*

!!! note
    For serialization is neccesary to use python `dataclasses`

## Deserialization

Deserialization could take place with an instance dataclass or the dataclass itself. Can return the dict representation or a new class instance.

```python title="Avro and avro-json deserialization"
import typing
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class Address(AvroModel):
    "An Address"
    street: str
    street_number: int


@dataclasses.dataclass
class User(AvroModel):
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.List[Address]

avro_binary = b"\x08john(\x02\x08test\x14\x00"
avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'

# return a new class instance!!
User.deserialize(avro_binary)
# >>> User(name='john', age=20, addresses=[Address(street='test', street_number=10)])

# return a python dict
User.deserialize(avro_binary, create_instance=False)
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

# return a new class instance!!
User.deserialize(avro_json_binary, serialization_type="avro-json")
# >>> User(name='john', age=20, addresses=[Address(street='test', street_number=10)])

# return a python dict
User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False)
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}
```

*(This script is complete, it should run "as is")*

### Deserialization using a different schema

To deserialize data encoded via a different schema, one can pass an optional `writer_schema: AvroModel | dict[str, Any]` attribute. It will be used by the **fastavro**s `schemaless_reader`.

```python title="Deserialization with different schemas"
@dataclass
class User(AvroModel):
    name: str
    age: int


@dataclass
class UserCompatible(AvroModel):
    name: str
    age: int
    nickname: Optional[str] = None

    class Meta:
        schema_name = "User"


user_data = {
    "name": "G.R. Emlin",
    "age": 52,
}

# serialize data with the User schema
>>> serialized_user = User(**user_data).serialize()

# deserialize user using a new, but compatible schema
>>> deserialized_user = UserCompatible.deserialize(serialized_user, writer_schema=User)
```

*(This script is complete, it should run "as is")*

## Custom Serialization

The `serialization/deserialization` process is built over [fastavro](https://github.com/fastavro/fastavro). If you want to use another library or a different process, you can override the base `AvroModel`:

```python title="Custom serialization"
import dataclasses

from dataclasses_avroschema import AvroModel, SerializationType


@dataclasses.dataclass
class MyAvroModel(AvroModel):

    ...

    def serialize(self, serialization_type: SerializationType = "avro") -> bytes:
        # Get the schema as a python dict
        schema = self.avro_schema_to_python()

        # instance as python dict
        data = self.asdict()

        # call your custom serialization withe the avro schema and the data
        return custom_serialization(schema, datam serialization_type=serialization_type)

    @classmethod
    def deserialize(
        cls, data: bytes, serialization_type: SerializationType = "avro", create_instance: bool = True
    ) -> typing.Union[typing.Dict, "AvroModel"]:
        # Get the schema as a python dict
        schema = cls.avro_schema_to_python()

        # get the python dict with the schema and the data (bytes)
        payload = custom_deserialize(data, schema, serialization_type=serialization_type)

        if create_instance:
            return from_dict(data_class=cls, data=payload, config=Config(check_types=False))
        return payload


# and then inherits from your custom AvroModel

@dataclasses.dataclass
class Address(MyAvroModel):
    "An Address"
    street: str
    street_number: int
```

## Encoding for unions with avro-json

When you have an `union` and you want to serialize a `payload` using `avro-json` you will notice that the `type` is added to each `union` field.
This is needed because after the serialization process you need to know the `type` in order to `deserialize`:

!!! warning annotate "Do not confuse json with avro-json!!"

```python title="Union encoding with avro-json example"
import typing
import dataclasses
import datetime
import uuid

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class UnionSchema(AvroModel):
    "Some Unions"
    first_union: typing.Union[str, int]
    logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]


my_union = UnionSchema(first_union=10, logical_union=datetime.datetime.now())


event = my_union.serialize(serialization_type="avro-json")

print(event)
# long is added to each field
>>> b'{"first_union": {"long": 10}, "logical_union": {"long": 1647971584847}}'

my_union.deserialize(event, serialization_type="avro-json")
# >>> UnionSchema(first_union=10, logical_union=datetime.datetime(2022, 3, 22, 17, 53, 4, 847000, tzinfo=datetime.timezone.utc))


# bad data
event_2 = b'{"first_union": 10, "logical_union": {"long": 1647971584847}}'

my_union.deserialize(event_2, serialization_type="avro-json")

File ~/Projects/dataclasses-avroschema/.venv/lib/python3.10/site-packages/fastavro/io/json_decoder.py:213, in AvroJSONDecoder.read_index(self)
    211     label = "null"
    212 else:
--> 213     label, data = self._current[self._key].popitem()
    214     self._current[self._key] = data
    215     # TODO: Do we need to do this?

AttributeError: 'int' object has no attribute 'popitem'
```

*(This script is complete, it should run "as is")*

## Utils

The library includes two utils to serialize/deserialize using the `fastavro` as backend

::: dataclasses_avroschema.serialization.serialize
    options:
        show_source: false

::: dataclasses_avroschema.serialization.deserialize
    options:
        show_source: false
