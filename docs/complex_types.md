# Complex Types

The following list represent the avro complex types mapped to python types:

=== "python <= 3.10"

    | Avro Type          | Python Type                                                        |
    | ------------------ | ------------------------------------------------------------------ |
    | enums              | enum.Enum, typing.Literal[str]                                |
    | arrays             | typing.List, typing.Tuple, typing.Sequence, typing.MutableSequence |
    | maps               | typing.Dict, typing.Mapping, typing.MutableMapping                 |
    | fixed              | types.confixed                                                     |
    | unions             | typing.Union                                                       |
    | unions with `null` | typing.Optional                                                    |
    | records            | Python Class                                                       |

=== "python >= 3.11"

    | Avro Type          | Python Type                                                        |
    | ------------------ | ------------------------------------------------------------------ |
    | enums              | str, enum.Enum, typing.Literal[str]                                |
    | arrays             | typing.List, typing.Tuple, typing.Sequence, typing.MutableSequence |
    | maps               | typing.Dict, typing.Mapping, typing.MutableMapping                 |
    | fixed              | types.confixed                                                     |
    | unions             | typing.Union                                                       |
    | unions with `null` | typing.Optional                                                    |
    | records            | Python Class                                                       |

## Enums

=== "python <= 3.10"

    ```python title="Enum example"
    import enum
    import dataclasses

    from dataclasses_avroschema import AvroModel


    class FavoriteColor(enum.Enum):
        BLUE = "Blue"
        YELLOW = "Yellow"
        GREEN = "Green"
        
        class Meta:
            doc = "A favorite color"
            namespace = "some.name.space"
            aliases = ["Color", "My favorite color"]


    @dataclasses.dataclass
    class User(AvroModel):
        "An User"
        favorite_color: FavoriteColor = FavoriteColor.BLUE


    User.avro_schema()

    '{
      "type": "record",
      "name": "User",
      "fields":
      [
        {
          "name": "favorite_color",
          "type":
          {
            "type": "enum",
            "name": "FavoriteColor",
            "symbols":
            [
              "Blue",
              "Yellow",
              "Green"
            ],
            "doc": "A favorite color",
            "namespace": "some.name.space",
            "aliases":
            ["Color", "My favorite color"]
          },
          "default": "Blue"
        }
      ],
      "doc": "An User"
    }'
    ```

=== "python >= 3.11"

    ```python title="Enum example"
    import enum
    import dataclasses

    from dataclasses_avroschema import AvroModel


    class FavoriteColor(str, enum.Enum):
        BLUE = "Blue"
        YELLOW = "Yellow"
        GREEN = "Green"
        
        @enum.nonmember
        class Meta:
            doc = "A favorite color"
            namespace = "some.name.space"
            aliases = ["Color", "My favorite color"]


    @dataclasses.dataclass
    class User(AvroModel):
        "An User"
        favorite_color: FavoriteColor = FavoriteColor.BLUE


    User.avro_schema()

    '{
      "type": "record",
      "name": "User",
      "fields":
      [
        {
          "name": "favorite_color",
          "type":
          {
            "type": "enum",
            "name": "FavoriteColor",
            "symbols":
            [
              "Blue",
              "Yellow",
              "Green"
            ],
            "doc": "A favorite color",
            "namespace": "some.name.space",
            "aliases":
            ["Color", "My favorite color"]
          },
          "default": "Blue"
        }
      ],
      "doc": "An User"
    }'
    ```

!!! info
    There are not restriction about `enum` names but is is highly recommended to use `pascalcase`

### Enums from typing.Literal of strigns

`typing.Literal[...]` can be used to indicate to type checkers that the annotated object has a value equivalent to one of the provided literals. If all `Literal arguments` are `string`, then for some use cases an `avro enum` as representation would make more sense in order to preserve the constraints (`Literal arguments` to `enum symbols`).

For this behaviour the attribute `convert_literal_to_enum` must be set to `True`

=== "Literal as avro enum"
    ```python
    import dataclasses
    import typing
    from dataclasses_avroschema import AvroModel

    @dataclasses.dataclass
    class MyModel(AvroModel):
        options: typing.Literal["four_4", "five_5"] = "four_4"
        optional_field: typing.Optional[typing.Literal["four_4", "five_5"]] = None

        class Meta:
            convert_literal_to_enum = True

    print(MyModel.avro_schema())

    {
      "type": "record",
      "name": "MyModel", "fields": [
        {"name": "options", "type": {"type": "enum", "name": "options", "symbols": ["four_4", "five_5"]}, "default": "four_4"},
        {"name": "optional_field", "type": ["null", {"type": "enum", "name": "optional_field", "symbols": ["four_4", "five_5"]}], "default": null}]
    }
    ```

=== "Literal as avro string"
    ```python
    import dataclasses
    import typing
    from dataclasses_avroschema import AvroModel

    @dataclasses.dataclass
    class MyModel(AvroModel):
        options: typing.Literal["four_4", "five_5"] = "four_4"
        optional_field: typing.Optional[typing.Literal["four_4", "five_5"]] = None

    print(MyModel.avro_schema())

    {
      "type": "record",
      "name": "MyModel",
      "fields": [
        {"name": "options", "type": "string", "default": "four_4"},
        {"name": "optional_field", "type": ["null", "string"], "default": null}
      ]
    }
    ```

### Repeated Enums

Sometimes we have cases where an `Enum` is used more than once with a particular class, for those cases the same `type` is used in order to generate a valid schema.
It is a good practice but *NOT* neccesary to a define the `namespace` on the repeated `type`.

=== "python <= 3.10"

    ```python
    import enum
    import dataclasses
    import typing

    from dataclasses_avroschema import AvroModel


    class TripDistance(enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"
            namespace = "trip"


    @dataclasses.dataclass
    class User(AvroModel):
        trip_distance: TripDistance
        optional_distance: typing.Optional[TripDistance] = None


    print(User.avro_schema())
    ```

=== "python >= 3.11"

    ```python
    import enum
    import dataclasses
    import typing

    from dataclasses_avroschema import AvroModel


    class TripDistance(str, enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        @enum.nonmember
        class Meta:
            doc = "Distance of the trip"
            namespace = "trip"


    @dataclasses.dataclass
    class User(AvroModel):
        trip_distance: TripDistance
        optional_distance: typing.Optional[TripDistance] = None


    print(User.avro_schema())
    ```

resulting in

```json
{
  "type": "record",
  "name": "User",
  "fields": [
    {
      "name": "trip_distance",
      "type": {
        "type": "enum",
        "name": "TripDistance",
        "symbols": [
          "Close",
          "Far"
        ],
        "doc": "Distance of the trip",
        "namespace": "trip"
      }
    },
    {
      "name": "optional_distance",
      "type": [
        "null",
        "trip.TripDistance"  // using the namespace and the TripDistance type
      ],
      "default": null
    }
  ],
  "doc": "User(trip_distance: __main__.TripDistance, optional_distance: Optional[__main__.TripDistance] = None)"
}
```

### Enums type level default

From `avro 1.9.0` it is possible to set `enum type level default`: *Enum type level default value is to deal with newly added symbols that the reader does not know about. This is for forward compatibility*.

```json title="Example"
{
  "type": "record",
  "name": "MyRecord",
  "fields": [
    {
      "name": "my_field",
      "type": {
        "type": "enum",
        "name": "MyEnum",
        "symbols": [
          "A",
          "B",
          "Unknown"
        ],
        /* 
         * Symbol default - for forward compatibility - 
         * new in Avro 1.9.0
         */
         "default": "Unknown"  
      },
      /*
       * Field default - for handle backwards compatibility
       */ 
      "default": "Unknown"    
    }
  ]
}
```

The question is: how can we set a `enum type level default`?. The answer is using the `class Meta`

=== "python <= 3.10"

    ```python
    import enum
    import dataclasses

    from dataclasses_avroschema import AvroModel


    class MyEnum(enum.Enum):
        A = "A"
        B = "B"
        UNKNOWN = "Unknown"

        class Meta:
            default = "Unknown"


    @dataclass
    class MyRecord(AvroModel):
        my_field: MyEnum = MyEnum.UNKNOWN
    ```

=== "python >= 3.11"

    ```python
    import enum
    import dataclasses

    from dataclasses_avroschema import AvroModel


    class MyEnum(str, enum.Enum):
        A = "A"
        B = "B"
        UNKNOWN = "Unknown"

        @enum.nonmember
        class Meta:
            default = "Unknown"


    @dataclass
    class User(AvroModel):
        my_field: MyEnum = MyEnum.UNKNOWN
    ```

!!! warning
    This is great because we achieve avro `FULL COMPATIBILITY`, however this can lead to confusing scenarios.
    Check the [discussion](https://github.com/marcosschroh/dataclasses-avroschema/issues/665#issuecomment-2225293099) for more insight

## Arrays

```python title="Array example"
import dataclasses
import typing

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class UserAdvance(AvroModel):
    "User advanced"
    pets: typing.List[str]
    cars: typing.List[str] = None
    favourites_numbers: typing.List[int] = dataclasses.field(default_factory=lambda: [7, 13])


UserAdvance.avro_schema()

'{
  "type": "record",
  "name": "UserAdvance",
  "fields": [
    {
      "name": "pets",
      "type": {
        "type": "array",
        "items": "string",
        "name": "pet"
      }
    },
    {
      "name": "cars",
      "type": {
        "type": "array",
        "items": "string",
        "name": "car"
      },
      "default": []
    },
    {
      "name": "favourites_numbers",
      "type": {
        "type": "array",
        "items": "long",
        "name": "favourites_number"
      },
      "default": [7, 13]
    }
  ],
  "doc": "User advanced"
}'
```

## Maps

```python title="Map example"
import dataclasses
import typing

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class UserAdvance(AvroModel):
    "User advanced"
    accounts_money: typing.Dict[str, float]
    cars_brand_total: typing.Dict[str, int] = None
    family_ages: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"father": 50})

UserAdvance.avro_schema()

'{
  "type": "record",
  "name": "UserAdvance",
  "fields": [
    {
      "name": "accounts_money",
      "type": {
        "type": "map",
        "values": "float",
        "name": "accounts_money"
      }
    },
    {
      "name": "cars_brand_total",
      "type": {
        "type": "map",
        "values": "long",
        "name": "cars_brand_total"
      },
      "default": {}
    },
    {
      "name": "family_ages",
      "type": {
        "type": "map",
        "values": "long",
        "name": "family_age"
      },
      "default": {"father": 50}
    }
  ],
  "doc": "User advanced"
}'
```

## Fixed

Fixed types in avro must specify one required attribute size  which specifies the number of bytes per value. Because the `fixed` type does not exist in python it is not possible to supply the required arguments directly in the type so dataclasses-avroschema provides a funtion to create fixed. The function types.confixed annotates the `types.Fixed` type and it adds the required attibutes.

### Arguments to confixed

The following arguments are available when using the confixed type function

- size (int): number of bytes per value
- aliases (List[str]):  a List of strings, providing alternate names (optional)
- namespace (str): a string that qualifies the name (optional);

```python title="Fixed example"
import typing
import dataclasses

from dataclasses_avroschema import AvroModel, types


@dataclasses.dataclass
class UserAdvance(AvroModel):
    md5: types.confixed(size=16, namespace='md5', aliases=["md5", "hash"])
    name: types.confixed(size=16) = b"u00ffffffffffffx"

UnionSchema.avro_schema()

{
  'type': 'record',
  'name': 'UserAdvance',
  'fields': [
    {'name': 'md5', 'type': {'type': 'fixed', 'name': 'md5', 'size': 16,'namespace': 'md5', 'aliases': ['md5', 'hash']}},
    {"name": "name", "type": {"type": "fixed", "name": "name", "size": 16}, "default": "u00ffffffffffffx"}
  ],
  'doc': 'UserAdvance(name: str, md5: dataclasses_avroschema.types.Fixed = 16)'}
```

## Unions

=== "python <= 3.9"

    ```python
    import typing
    import dataclasses
    import datetime
    import uuid

    from dataclasses_avroschema import AvroModel


    @dataclasses.dataclass
    class UnionSchema(AvroModel):
        "Some Unions"
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        second_union: typing.Union[str, int] = "test"
        third_union: typing.Union[int, str] = 'STRING TYPE'

    UnionSchema.avro_schema()
    ```

=== "python3.10"

    ``` python
    import typing
    import dataclasses
    import datetime
    import uuid

    from dataclasses_avroschema import AvroModel


    @dataclasses.dataclass
    class UnionSchema(AvroModel):
        "Some Unions"
        first_union: str | int
        logical_union: datetime.datetime | datetime.date | uuid.uuid
        second_union: str | int = "test"
        third_union: int | str = 'STRING TYPE'

    UnionSchema.avro_schema()
    ```

```json title="result"
{
  "type": "record",
  "name": "UnionSchema",
  "fields": [
  {"name": "first_union", "type": ["string", "long"]},
  {"name": "logical_union", "type": [
    {"type": "long", "logicalType": "timestamp-millis"},
    {"type": "long", "logicalType": "date"},
    {"type": "string", "logicalType": "uuid"}]},
  {"name": "second_union", "type": ["string", "long"], "default": "test"},
  {"name": "third_union", "type": ["string", "long"], "default": "STRING TYPE"}],
  "doc": "Some Unions"
}
```  

### Union with Records

=== "python <= 3.9"

    ```python
    import dataclasses
    from dataclasses_avroschema import AvroModel


    @dataclasses.dataclass
    class Bus(AvroModel):
        "A Bus"
        engine_name: str

        class Meta:
            namespace = "types"


    @dataclasses.dataclass
    class Car(AvroModel):
        "A Car"
        engine_name: str

        class Meta:
            namespace = "types"


    @dataclasses.dataclass
    class UnionSchema(AvroModel):
      "Some Unions"
      lake_trip: typing.Union[Bus, Car]
      river_trip: typing.Union[Bus, Car] = None
      mountain_trip: typing.Union[Bus, Car] = dataclasses.field(
          default_factory=lambda: Bus("engine_name": "honda"))

    UnionSchema.avro_schema()
    ```
  
=== "python3.10"

    ```python
    import dataclasses
    from dataclasses_avroschema import AvroModel


    @dataclasses.dataclass
    class Bus(AvroModel):
        "A Bus"
        engine_name: str

        class Meta:
            namespace = "types"


    @dataclasses.dataclass
    class Car(AvroModel):
        "A Car"
        engine_name: str

        class Meta:
            namespace = "types"


    @dataclasses.dataclass
    class UnionSchema(AvroModel):
      "Some Unions"
      lake_trip: Bus | Car
      river_trip: Bus | Car | None = None
      mountain_trip: Bus | Car = dataclasses.field(
          default_factory=lambda: Bus("engine_name": "honda"))

    UnionSchema.avro_schema()
    ```

```json title="result"
{
  "type": "record",
  "name": "UnionSchema",
  "fields": [
    {
      "name": "lake_trip",
      "type": [
        {
          "type": "record",
          "name": "Bus",
          "fields": [
            {
              "name": "engine_name",
              "type": "string"
            }
          ],
          "doc": "A Bus"
        },
        {
          "type": "record",
          "name": "Car",
          "fields": [
            {
              "name": "engine_name",
              "type": "string"
            }
          ],
          "doc": "A Car"
        }
      ]
    },
    {
      "name": "river_trip",
      "type": [
        "null",
        "types.Bus",
        "types.Car"
      ]
      "default": null
    },
    {
      "name": "mountain_trip",
      "type": [
        "types.Bus",
        "types.Car"
      ],
      "default": {"engine_name": "honda"}
    }
  ],
  "doc": "Some Unions"
}
```

!!! note
    From python 3.10 you can use [union type expressions](https://docs.python.org/3.10/library/stdtypes.html#types-union) using the `|` operator

### Unions with typing.Optional

`typing.Optional[Any]` is translated as an optional Union: `typing.Union[Any, NoneType]` where `NoneType`
is always at the end

=== "python <= 3.9"

    ```python
    import typing
    import dataclasses

    from dataclasses_avroschema import AvroModel
    from dataclasses import dataclass, field


    @dataclasses.dataclass
    class X(AvroModel):
        y: typing.Optional[typing.List[int]]


    X.avro_schema()
    ```

=== "python3.10"

    ```python
    import typing
    import dataclasses

    from dataclasses_avroschema import AvroModel
    from dataclasses import dataclass, field


    @dataclasses.dataclass
    class X(AvroModel):
        y: typing.List[int] | None


    X.avro_schema()
    ```

```json title="result"
{
    "type": "record",
    "name": "X",
    "fields": [
        {"name": "y", "type": [{"type": "array", "items": "long", "name": "y"}, "null"]}
    ],
    "doc": "X(y: Union[List[int], NoneType])"
}
```
