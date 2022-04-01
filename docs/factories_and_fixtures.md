[Dataclasses Avro Schema](https://github.com/marcosschroh/dataclasses-avroschema) also includes a `factory` feature, so you can generate `fast` python instances and use them, for example, to test your data streaming pipelines. Instances can be genrated using the `fake` method.

```python title="Basic usage"
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

*(This script is complete, it should run "as is")*
