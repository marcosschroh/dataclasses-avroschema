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

Deserialization could take place with an instance dataclass or the dataclass itself

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

User.deserialize(avro_binary)
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

User.deserialize(avro_json_binary, serialization_type="avro-json")
# >>> {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}
```
