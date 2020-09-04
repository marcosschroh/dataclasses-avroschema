With `dataclasses-avroschema` you can generate `fake` instances when you want to perform fast testing or maybe you want to do `e2e` tests in your data streaming pipelines. Fake instances can be genrated calling the `fake` method.

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


Address.fake()
# >>>> Address(street='PxZJILDRgbXyhWrrPWxQ', street_number=2067)

User.fake()
# >>>> User(name='VGSBbOGfSGjkMDnefHIZ', age=8974, addresses=[Address(street='vNpPYgesiHUwwzGcmMiS', street_number=4790)])
```
