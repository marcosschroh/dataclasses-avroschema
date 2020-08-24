# Examples of dataclasses-avroschema

You will find a series of example about how to use [dataclasses-avroschema](https://github.com/marcosschroh/dataclasses-avroschema) and the integration with python drivers like [aiokafka](https://github.com/aio-libs/aiokafka), [confluent](https://github.com/confluentinc/confluent-kafka-python) and [kafka-python](https://github.com/dpkp/kafka-python).

## Requirements

`python 3.7+ docker docker-compose`

## Installation

1. `python3.7 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`

## Run the examples

1. `make kafka-cluster` to start the kafka cluster (kafka and zookeeper)
2. In the same path but in a different terminal execute `make start-aiokafka-example` in order to start the producer/consumer for `aiokafka` driver (async)
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

[Example of dataclasses-avroschema and aiokafka](https://github.com/marcosschroh/dataclasses-avroschema/blob/feat/return-instance-after-deserialization/examples/aiokafka_example.py)

[Example of dataclasses-avroschema and confluent](https://github.com/marcosschroh/dataclasses-avroschema/blob/feat/return-instance-after-deserialization/examples/aiokafka_example.py)

[Example of dataclasses-avroschema and kafka-python](https://github.com/marcosschroh/dataclasses-avroschema/blob/feat/return-instance-after-deserialization/examples/aiokafka_example.py)
