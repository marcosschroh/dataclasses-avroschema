# Examples of dataclasses-avroschema

You will find a series of example about how to use [dataclasses-avroschema](https://github.com/marcosschroh/dataclasses-avroschema) and the integration with python drivers like [aiokafka](https://github.com/aio-libs/aiokafka) and [kafka-python](https://github.com/dpkp/kafka-python) in the case of `kafka`.

## Requirements

`python 3.10+ poetry docker docker-compose`

## Kafka examples

As examples you will find how to `serialize/deserialize` python dataclasses using the `AvroModel` provided by `dataclasses-avroschema` and how to produce/consume events using specifics python kafka drivers.

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

### Cluster setup

1. `cd kafka-examples`
1. `make kafka-cluster` to start the kafka cluster (kafka and zookeeper)
1. `make create-example-topics` to create the example topics

### aiokafka example

In the file [app.py](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/examples/kafka-examples/aiokafka-example/aiokafka_example/app.py) you will find the simplest `async` example where the model instance is serialize and send it throught kafka. A consumer receives the event and deserialized it returning a new model instance.

1. `cd aiokafka-example`
1. `poetry install`
1. `poetry run app`
1. To stop the producer/consumer use `Ctrl + c`

### kafka-python example

In the file [kafka-examples/kafka_python_example/app.py](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/examples/kafka-examples/kafka-python-example/kafka_python_example/app.py) you will find a a similar example as with `aiokafka` but in this case `synchronous` and using `avro-json` serialization instead of `avro` serialization.

1. `cd kafka-python-example`
1. `poetry install`
1. `poetry run app`
1. To stop the producer/consumer use `Ctrl + c`

### dataclasses-avroschema and Schema evolution

In the file [app.py](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/examples/kafka-examples/schema-evolution-example/schema_evolution_example/app.py) you will find an example of how the schema evolution works. In this case we show the `FULL` compatibility, user the previous model and performing the deserialization with the `User.v2` which has an extra optional field called `has_pets`. Run it with `make schema-evolution-example`

1. `cd schema-evolution-example`
1. `poetry install`
1. `poetry run app`
1. To stop the producer/consumer use `Ctrl + c`
