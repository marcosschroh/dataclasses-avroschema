# Examples of dataclasses-avroschema with RabbitMQ

You will find an example of how to use [dataclasses-avroschema](https://github.com/marcosschroh/dataclasses-avroschema) and the integration with the python drivers [pika](https://github.com/pika/pika)

## Requirements

`python 3.8+ poetry docker docker-compose`

### Cluster setup

1. `cd rabbitmq-examples`
1. `docker-compose up` to start the rabbitmq cluster

## Examples

As examples you will find how to serialize/deserialize python dataclasses using the `AvroModel` provided by `dataclasses-avroschema` and how to produce/consume events using specifics python kafka drivers.

The model is for the examples is the following:

```python
from dataclasses import dataclass
import typing
import enum

from dataclasses_avroschema import AvroModel


class FavoriteColor(enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


@dataclass
class UserModel(AvroModel):
    "An User"
    name: str
    age: int
    favorite_colors: FavoriteColor = FavoriteColor.BLUE
    country: str = "Argentina"
    address: typing.Optional[str] = None

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]
```

### dataclasses-avroschema and redis streams with walrus

In the file [app.py](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/examples/rabbitmq-examples/rabbitmq-pika/rabbitmq_pika/app.py) you will find a the simplest use case of `rabbitmq streams` using the driver `pike`.

1. `cd rabbitmq-examples/rabbitmq-pika`
1. `poetry install`
1. `poetry run app`
1. To stop the producer/consumer use `Ctrl + c`
