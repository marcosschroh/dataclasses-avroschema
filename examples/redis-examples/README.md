# Examples of dataclasses-avroschema

You will find an example of how to use [dataclasses-avroschema](https://github.com/marcosschroh/dataclasses-avroschema) and the integration with the python drivers [walrus](https://github.com/coleifer/walrus)

## Requirements

`python 3.10+ poetry docker docker-compose`

### Cluster setup

1. `cd redis-examples`
1. `make redis-cluster` to start the redis cluster

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

In the file [app.py](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/examples/redis-examples/redis-streams-example/redis_streams_example/app.py) you will find a the simplest use case of `redis streams` using the driver `walrus`. We create a consumer group and messages are read one by one.

1. `cd redis-examples/redis-streams-example`
1. `poetry install`
1. `poetry run app`
1. To stop the producer/consumer use `Ctrl + c`
