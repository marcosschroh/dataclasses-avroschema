Is possible to `serialize/deserialize` with the correspondent avro schema generated and the dataclass.
In both cases we can do it with `avro` or `avro-json`.

### Serialization

For serialization is neccesary to use python class/dataclasses instance:

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

### Deserialization

Deserialization could take place with an instance dataclass or the dataclass itself. Can return the dict representation or a new class instance.

```python
import typing

from dataclasses_avroschema import AvroModel


class Address(AvroModel):
    "An Address"
    street: str
    street_number: int

class User(AvroModel):
    "User with multiple Address"
    name: str
    age: int
    addresses: typing.List[Address]

avro_binary = b"\x08john(\x02\x08test\x14\x00"
avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'

# return a new class instance!!
User.deserialize(avro_binary)
# >>>> User(name='john', age=20, addresses=[Address(street='test', street_number=10)])

# return a python dict
User.deserialize(avro_binary, create_instance=False)
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

# return a new class instance!!
User.deserialize(avro_json_binary, serialization_type="avro-json")
# >>>> User(name='john', age=20, addresses=[Address(street='test', street_number=10)])

# return a python dict
User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False)
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}
```

### Custom Serialization

The `serialization/deserialization` process is built over [fastavro](https://github.com/fastavro/fastavro). If you want to use another library or a different process, you can override the base `AvroModel`:

```python
from dataclasses_avroschema import AvroModel


class MyAvroModel(AvroModel):

    ...

    def serialize(self, serialization_type: str = AVRO) -> bytes:
        # Get the schema as a python dict
        schema = self.avro_schema_to_python()

        # instance as python dict
        data = self.asdict()

        # call your custom serialization withe the avro schema and the data
        return custom_serialization(schema, datam serialization_type=serialization_type)

    @classmethod
    def deserialize(
        cls, data: bytes, serialization_type: str = AVRO, create_instance: bool = True
    ) -> typing.Union[typing.Dict, "AvroModel"]:
        # Get the schema as a python dict
        schema = cls.avro_schema_to_python()

        # get the python dict with the schema and the data (bytes)
        payload = custom_deserialize(data, schema, serialization_type=serialization_type)

        if create_instance:
            return from_dict(data_class=cls, data=payload, config=Config(check_types=False))
        return payload


# and then inherits from your custom AvroModel

class Address(MyAvroModel):
    "An Address"
    street: str
    street_number: int
```
