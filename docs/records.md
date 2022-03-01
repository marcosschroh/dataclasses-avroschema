## Records

Mapped as a Python class

There are some special avro attributes like `aliases`, `namespace` and `doc` (both not required) that can be specified in a record type.

The `doc` attribute can be set via the docstring class. The `aliases` and `namespaces` must be set using `Class Meta`.

```python
from dataclasses_avroschema import AvroModel


class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3

    class Meta:
        namespace = "test.com.ar/user/v1"
        aliases = ["User", "My favorite User"]

User.avro_schema()

'{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "long"},
    {"name": "has_pets", "type": "boolean", "default": false},
    {"name": "money", "type": "double", "default": 100.3}
  ],
  "doc": "My User Class",
  "namespace": "test.com.ar/user/v1",
  "aliases": ["User", "My favorite User"]
}'
```

*(This script is complete, it should run "as is")*

### Class Meta

The `class Meta` is used to specify schema attributes that are not represented by the class fields like `namespace`, `aliases` and whether to include the `schema documentation`. One can also provide a custom schema name (the default is the class' name) via `schema_name` attribute and `alias_nested_items` when you have nested items and you want to use custom naming for them.

```python
class Meta:
    schema_name = "Name other than the class name"
    schema_doc = False
    namespace = "test.com.ar/user/v1"
    aliases = ["User", "My favorite User"]
    alias_nested_items = {"address": "Address"}
```

`schema_doc (boolean)`: Whether include the `schema documentation` generated from `docstrings`. Default `True`
`namespace (optional[str])`: Schema namespace. Default `None`
`aliases (optional[List[str]])`: Schema aliases. Default `None`
`alias_nested_items (optional[Dict[str, str]])`: Nested items names

### Record to json and dict 

You can get the `json` and `dict` representation of your instance using `to_json` and `to_dict` methods:

```python
import dataclasses

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class User(AvroModel):
    "My User Class"
    name: str
    age: int
    has_pets: bool = False
    money: float = 100.3


user = User(name="Bond", age=50)

user.to_json()
# >>> '{"name": "Bond", "age": 50, "has_pets": false, "money": 100.3}'

user.to_dict()
# >>> {'name': 'Bond', 'age': 50, 'has_pets': False, 'money': 100.3}
```

*(This script is complete, it should run "as is")*

### Validation

Python classes that inheritance from `AvroModel` has a `validate` method. This method `validates` whether the instance data matches
the schema that it represents, for example:

```python
from dataclasses import dataclass


from dataclasses_avroschema import AvroModel


@dataclass
class User(AvroModel):
    name: str
    age: int
    has_pets: bool
    money: float
    encoded: bytes

# this creates a proper instance
user_instance = User(
    name="a name",
    age=10,
    has_pets=True,
    money=0,
    encoded=b'hi',
)
assert user_instance.validate()

# set 1 to the name attribute and the fastavro validation should fail
# This is possible because in dataclasses there is not restriction,
# but at the moment of using pydantic this will change
user_instance.name = 1
with pytest.raises(ValidationError) as exc:
    assert user_instance.validate()

assert json.loads(str(exc.value)) == ["User.name is <1> of type <class 'int'> expected string"]
```

*(This script is complete, it should run "as is")*
