## Avro Schemas and Python Class

### What is Apache Avro?

Avro is a row-oriented remote procedure call and data serialization framework developed within Apache's Hadoop project. It uses JSON for defining data types and protocols, and serializes data in a compact binary format. Avro uses a `schema` to structure the data that is being encoded. It has two different types of schema languages; one for human editing `(Avro IDL)` and another which is more machine-readable based on `(JSON)`

### Goal

Our goal is to come up with an `avro schema` from `Python classes`.
We can think a `avro Record` as an analogous to a `python class`, but first, let's explaine what a `record` is.

### Records

Records are one of the `Complex Types` in avro. It use the type name `record` and support three attributes.

* name: a JSON string providing the name of the record (required).
* namespace: a JSON string that qualifies the name;
* doc: a JSON string providing documentation to the user of this schema (optional).
* aliases: a JSON array of strings, providing alternate names for this record (optional).
* fields: a JSON array, listing fields (required). Each field is a JSON object with the following attributes:
    * name: a JSON string providing the name of the field (required), and
    * doc: a JSON string describing this field for users (optional).
    * type: A JSON object defining a schema, or a JSON string naming a record definition (required).
    * default: A default value for this field, used when reading instances that lack this field (optional). Permitted    values depend on the field's schema type, according to the table below. Default values for union fields correspond to the first schema in the union. Default values for bytes and fixed fields are JSON strings, where Unicode code points 0-255 are mapped to unsigned 8-bit byte values 0-255.
    * order: specifies how this field impacts sort ordering of this record (optional). Valid values are "ascending" (the default), "descending", or "ignore". For more details on how this is used, see the the sort order section below.
    * aliases: a JSON array of strings, providing alternate names for this field (optional).

For example, a User may be defined with:

```python
{
    "type": "record",
    "name": "User",
    "fields" : [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"},
        {"name": "has_pets", "type": "boolean"},
        {"name": "money", "type": "float"}
    ]
}
```

### From a Python class to the Avro Schema

Image that you have to define the previous `User` schema but you do not know avro, you know python:

```python title="Generate the avro schema from a class"
import dataclasses
from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class User(AvroModel):
    name: str
    age: int
    has_pets: bool
    money: float

User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "has_pets", "type": "boolean"},
    {"name": "money", "type": "float"}
  ],
  "doc": "User(name: str, age: int, has_pets: bool, money: float)"
}'
```

*(This script is complete, it should run "as is")*

or create a python dictionary

```python title="Avro schema to python"
User.avro_schema_to_python()

{
    "type": "record",
    "name": "User",
    "doc": "An User",
    "namespace": "User.v1",
    "aliases": ["user-v1", "super user"],
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "long"},
        {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}},
        {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}},
        {"name": "favorite_color", "type": {"type": "enum", "name": "favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}},
        {"name": "country", "type": "string", "default": "Argentina"},
        {"name": "address", "type": ["null", "string"], "default": None}
    ],
}
```

and that is it!! Each python field is related with a avro type. You can find the field relationships [here](https://marcosschroh.github.io/dataclasses-avroschema/fields_specification/):
