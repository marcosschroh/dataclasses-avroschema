## Avro Fields and Python Fields

Apache Avro has `Primitive Types` and `Complex Types`, so we need to match these types with python types.

## Primitive Types and python representation

The set of primitive type names is:

* null: no value
* boolean: a binary value
* int: 32-bit signed integer
* long: 64-bit signed integer
* float: single precision (32-bit) IEEE 754 floating-point number
* double: double precision (64-bit) IEEE 754 floating-point number
* bytes: sequence of 8-bit unsigned bytes
* string: unicode character sequence

So, the previous types can be matched to:

| Avro Type | Python Type |
|-----------|-------------|
| string    |     str     |
| int       |     int     |
| long      |     int     |
| boolean   |     bool    |
| float     |     float   |
| double    |     float   |
| null      |     None    |
| bytes     |     wip     |

Example:

```python
class User:
    name: str
    age: int
    has_pets: bool
    money: float
    
    # some with default values
    country: str = "Argentina"
    address: str = None
    total_houses: int = 1
    has_car: bool = False
```


## Complex Types

Avro supports six kinds of complex types: records, enums, arrays, maps, unions and fixed.

### Enums

Enums use the type name "enum" and support the following attributes:

* name: a JSON string providing the name of the enum (required).
* namespace: a JSON string that qualifies the name;
* aliases: a JSON array of strings, providing alternate names for this enum (optional).
* doc: a JSON string providing documentation to the user of this schema (optional).
* symbols: a JSON array, listing symbols, as JSON strings (required). All symbols in an enum must be unique; duplicates are prohibited. Every symbol must match the regular expression [A-Za-z_][A-Za-z0-9_]* (the same requirement as for names).

For example, playing card suits might be defined with:

```python
{ "type": "enum",
  "name": "Suit",
  "symbols" : ["SPADES", "HEARTS", "DIAMONDS", "CLUBS"]
}
```

The `enum` type is mapped to a python `tuple`.

Example:

```python
class User:
    ...
    favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
```

* When we want to define a `enum` type we should specify a default value because we need to define the `symbols`
  In future version we will have a custom enum type to avoid this

### Arrays

Arrays use the type name "array" and support a single attribute:

* items: the schema of the array's items.

For example, an array of strings is declared with:

```python
{"type": "array", "items": "string"}
```

The `array` type is mapped to a python `list`.

Example:

```python
   class UserAdvance:
    ...
    pets: typing.List[str]
    cars: typing.List[str] = None
```

### Maps

Maps use the type name "map" and support one attribute:

* values: the schema of the map's values.

Map keys are assumed to be strings.

For example, a map from string to long is declared with:

```python
{"type": "map", "values": "long"}
```

The `array` type is mapped to a python `dict` where all the keys should be `string`.

Example:

```python
class UserAdvance:
    ...
    accounts_money: typing.Dict[str, float]
    cars_brand_total: typing.Dict[str, int] = None
```

### Records

Records use the type name "record" and will represent the "Schema".


### Avro Field and Python Types Summary

| Avro Type | Python Type |
|-----------|-------------|
| string    |     str     |
| int       |     int     |
| long      |     int     |
| boolean   |     bool    |
| float     |     float   |
| null      |     None    |
| double    |     wip     |
| bytes     |     wip     |
| enum      |     tuple   |
| array     |     list    |
| map       |     dict    |
| record    | Python class|


