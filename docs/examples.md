# Examples

Under [examples](https://github.com/marcosschroh/dataclasses-avroschema/tree/master/examples) folder you can find 4 differents examples, one with [aiokafka](https://github.com/aio-libs/aiokafka) (`async`) showing the simplest use case when a `AvroModel` instance is serialized and sent it thorught kafka, and the event is consumed.
The other two examples are `sync` using the [kafka-python](https://github.com/dpkp/kafka-python) driver, where the `avro-json` serialization and `schema evolution` (`FULL` compatibility) is shown. The last example is a redis example with the python drivers [walrus](https://github.com/coleifer/walrus)

## Kafka examples

```python title="aiokafka example"
--8<-- "examples/kafka-examples/aiokafka-example/aiokafka_example/app.py"
```

*(This script is complete, it should run "as is")*

```python title="kafka-python example"
--8<-- "examples/kafka-examples/kafka-python-example/kafka_python_example/app.py"
```

*(This script is complete, it should run "as is")*

```python title="schema evolution example"
--8<-- "examples/kafka-examples/schema-evolution-example/schema_evolution_example/app.py"
```

*(This script is complete, it should run "as is")*

## Redis examples

Minimal redis [example](https://github.com/marcosschroh/dataclasses-avroschema/tree/master/examples#dataclasses-avroschema-and-redis-streams-with-walrus) using `redis streams` with [walrus](https://github.com/coleifer/walrus) driver.

```python title="redis streams example"
--8<-- "examples/redis-examples/redis-streams-example/redis_streams_example/app.py"
```

*(This script is complete, it should run "as is")*

## RabbitMQ examples

Minimal rabbitmq [example](https://github.com/marcosschroh/dataclasses-avroschema/blob/master/examples/rabbitmq-examples/rabbitmq-pika/rabbitmq_pika/app.py) with [pika](https://github.com/pika/pika) driver.

```python title="rabbitmq example"
--8<-- "examples/rabbitmq-examples/rabbitmq-pika/rabbitmq_pika/app.py"
```

*(This script is complete, it should run "as is")*
