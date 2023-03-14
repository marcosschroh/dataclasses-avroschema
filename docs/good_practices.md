# Streaming

## Schema server and AvroModel

First, let's clarify what a schema server is: It is a `central place/repository` that contains schemas with formats like `avro`, `json` or `protobuf`, with the purpose of exposing them through an `API`, so applications can access them and `serialize/deserialize` events. The schema server could have a `RESTful` interface so tasks like `create`, `delete` `get` schemas can be performed easily. 

In a `pythonic world`, you wouldn't need a `schema server` because using only the `AvroModel` will be enough as all the teams in your organization will use the same models, but this is not always the case. Somethimes, in big companies teams use different programming languages to talk the streaming layer, like `python`, `java`, `go`, etc. In this sense, you need a way to share `schemas` and you will need a `schema server`, otherwise it will be really hard to maintain the whole proccess.

If you have a `Schema Server` and you want to use `AvroModel`, I would recommend you to add the `schema_id` in the `Model.Meta` that matches the schema in the `schema server`:


```python title="Include schema_id in Meta"
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    class Meta:
        schema_id = "https://my-schema-server/users/schema.avsc" # or in a Concluent way: https://my-schema-server/schemas/ids/{int: id}
```

The purpose of the `schema_id` is to give a fast notion what the model is representing. Also, could be used as `documentation`

## Include event metadata

`avro schemas` are used widely in `streaming` to `serialize` events, and with `dataclasses-avroschemas` it is straigtforward. Once 
that you have the event, it is a good practice to also add the `event metadata` at the moment of `producing` so `consumers` will know what to do.

Event metadata:

* `content-type` or `serialization-type`: represents the way that the event was serialized. This could be `avro` or `avro-json` for example.
* `schema-id`: represents the `schema-id` that was used to serialize the event if exist.

```python title="Produce event with metadata"
import asyncio
import dataclasses
from dataclasses_avroschema import AvroModel
from aiokafka import AIOKafkaProducer


@dataclasses.dataclass
class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    class Meta:
        schema_id = "https://my-schema-server/users/schema.avsc" # or in a Confluent way: https://my-schema-server/schemas/ids/{int: id}


async def produce():
    # Naive example of producing an event

    producer = AIOKafkaProducer(bootstrap_servers='localhost:9092')
    await producer.start()

    user = User("Bond", age="50")
    
    # create the event
    event = user.serialize()
    headers = [
        ("content-type": b"avro"),
        ("schema-id": User.Meta.schema_id.encode()),
    ]

    await producer.send_and_wait("my_topic", value=event, headers=headers)
    await producer.stop()


if __name__ == "__main__":
    asyncio.run(produce)
```

## Define Namespaces

When there are types that are used more than once in a schema, for example `records` and `enums` it is a good practice to define `namespace` for the repeated type.
This will allow you to identify more easily the `types`, specially if you have all the schemas in a `schema server` like `confluent`.

Uses cases:

- [Reusing types with records](https://marcosschroh.github.io/dataclasses-avroschema/schema_relationships/#avoid-name-collision-in-multiple-relationships)
- [Reusing types with enums](https://marcosschroh.github.io/dataclasses-avroschema/complex_types/#repeated-enums)
