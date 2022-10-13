# Factories and Fixtures

[Dataclasses Avro Schema](https://github.com/marcosschroh/dataclasses-avroschema) also includes a `factory` feature, so you can generate `fast` python instances and use them, for example, to test your data streaming pipelines. Instances can be genrated using the `fake` method.

```python title="Basic usage"
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


Address.fake()
# >>>> Address(street='PxZJILDRgbXyhWrrPWxQ', street_number=2067)

User.fake()
# >>>> User(name='VGSBbOGfSGjkMDnefHIZ', age=8974, addresses=[Address(street='vNpPYgesiHUwwzGcmMiS', street_number=4790)])
```

*(This script is complete, it should run "as is")*

## Providing data to the factory

It is also possible to provide data as `keyword arguments` to the factory using the `fake` method.

```python
import typing
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class UserAdvance(AvroModel):
    name: str
    age: int
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    has_car: bool = False
    country: str = "Argentina"
    address: typing.Optional[str] = None


user = UserAdvance.fake(name="bond", age=50, pets=["dog", "cat"])
assert user.name == "bond"
assert user.age == 50
assert user.pets == ["dog", "cat"]

print(user)
# >>>> UserAdvance(name='bond', age=50, pets=['dog', 'cat'], accounts={'uVITaqdTStKhsdHFqIdM': 4201}, has_car=True, country='cirJWyuMaXoBqEmxbdML', address='qGhXKxAFfIxzAMZdkhrk')
```

*(This script is complete, it should run "as is")*
