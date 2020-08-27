# Examples of dataclasses-avroschema

You will find a series of example about how to use [dataclasses-avroschema](https://github.com/marcosschroh/dataclasses-avroschema) and the integration with python drivers like [aiokafka](https://github.com/aio-libs/aiokafka) and [kafka-python](https://github.com/dpkp/kafka-python).

## Requirements

`python 3.7+ docker docker-compose`

## Installation

1. `python3.7 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`

## Run the examples

1. `make kafka-cluster` to start the kafka cluster (kafka and zookeeper)
2. In the same path but in a different terminal execute `make aiokafka-example` in order to start the producer/consumer for `aiokafka` driver (async)
3. To stop the producer/consumer use `Ctrl + c`

## Examples

As examples you will find how to serialize/deserialize python dataclasses using the `AvroModel` provided by `dataclasses-avroschema` and how to produce/consume events using specifics python kafka drivers.

The model is for the examples is the following:

```python
@dataclass
class UserModel(AvroModel):
    "An User"
    name: str
    age: int
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"], default="BLUE")
    country: str = "Argentina"
    address: str = None

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]
```

### dataclasses-avroschema and aiokafka

In the file [aiokafka_example.py](https://github.com/marcosschroh/dataclasses-avroschema/blob/feat/return-instance-after-deserialization/examples/aiokafka_example.py) you will find the simplest `async` example where the model instance is serialize and send it throught kafka. A consumer receives the event and deserialized it returning a new model instance. Run it with `make aiokafka-example`

### dataclasses-avroschema and kafka-python

In the file [kafka_python_example.py](https://github.com/marcosschroh/dataclasses-avroschema/blob/feat/return-instance-after-deserialization/examples/kafka_python_example.py) you will find a a similar example as with `aiokafka` but in this case `synchronous` and using `avro-json` serialization instead of `avro` serialization. Run it with `make kafka-python-example`

### dataclasses-avroschema and Schema evolution

In the file [schema_evolution_example.py](https://github.com/marcosschroh/dataclasses-avroschema/blob/feat/return-instance-after-deserialization/examples/schema_evolution_example.py) you will find an example of how the schema evolution works. In this case we show the `FULL` compatibility, user the previous model and performing the deserialization with the `User.v2` which has an extra optional field called `has_pets`. Run it with `make schema-evolution-example`
