import json
import dataclasses
import typing

from collections import OrderedDict

from dataclasses_avroschema import schema_generator


BOOLEAN = "boolean"
NULL = "null"
INT = "int"
FLOAT = "float"
BYTES = "bytes"
STRING = "string"
ARRAY = "array"
ENUM = "enum"
MAP = "map"


PYTHON_TYPE_TO_AVRO = {
    bool: BOOLEAN,
    None: NULL,
    int: INT,
    float: FLOAT,
    bytes: BYTES,
    str: STRING,
    list: ARRAY,
    tuple: ENUM,
    dict: MAP,
}

# excluding tuple because is a container
PYTHON_INMUTABLE_TYPES = (str, int, bool, float, bytes)

PYTHON_PRIMITIVE_CONTAINERS = (list, tuple, dict)

PYTHON_PRIMITIVE_TYPES = PYTHON_INMUTABLE_TYPES + PYTHON_PRIMITIVE_CONTAINERS

PythonPrimitiveTypes = typing.Union[str, int, bool, float, list, tuple, dict]


@dataclasses.dataclass
class Field:
    name: str
    type: typing.Any  # store the python type
    default: typing.Any = dataclasses.MISSING

    # for avro array field
    items_type: typing.Any = None

    # for avro enum field
    symbols: typing.Any = None

    # for avro map field
    values_type: typing.Any = None

    # avro type storing
    avro_type: typing.Any = None

    def __post_init__(self):
        if isinstance(self.type, typing._GenericAlias):
            # means that could be a list, tuple or dict
            origin = self.type.__origin__

            if origin is list:
                # because avro can have only one type, we take the first one
                items_type = self.type.__args__[0]

                if items_type in PYTHON_PRIMITIVE_TYPES:
                    self.items_type = PYTHON_TYPE_TO_AVRO[items_type]
                else:
                    # means is a custom type
                    self.items_type = schema_generator.SchemaGenerator(items_type).avro_schema_to_python()
            elif origin is tuple:
                self.symbols = list(self.default)
            elif origin is dict:
                # because avro can have only one type, we take the first one
                self.values_type = PYTHON_TYPE_TO_AVRO[self.type.__args__[1]]
            else:
                # we do not accept any other typing._GenericAlias like a set
                # we should raise an exception
                raise ValueError(
                    f"Invalid Type for field {self.name}. Accepted types are list, tuple or dict")

            self.type = origin

    @property
    def to_avro_type(self) -> PythonPrimitiveTypes:
        if self.type in PYTHON_PRIMITIVE_TYPES:
            avro_type = PYTHON_TYPE_TO_AVRO.get(self.type)

            if self.default is not dataclasses.MISSING and self.type is not tuple:
                if self.default is not None:
                    return [avro_type, NULL]
                # means that default value is None
                return [NULL, avro_type]

            return avro_type
        else:
            # we need to see what to to when is a custom type
            # is a record schema
            return schema_generator.SchemaGenerator(self.type).avro_schema_to_python()

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.type in PYTHON_INMUTABLE_TYPES:
                if self.default is None:
                    return NULL
                return self.default
            elif self.type is list:
                if self.default is None:
                    return []

                assert isinstance(self.default, list), f"List is required as default for field {self.name}"
                return self.default
            elif self.type is dict:
                if self.default is None:
                    return {}

                assert isinstance(self.default, dict), f"Dict is required as default for field {self.name}"
                return self.default

    def render(self) -> OrderedDict:
        """
        Render the fields base on the avro field

        At least will have name and type.

        returns:
            OrderedDict(
                ("name", "a name"),
                ("type", "a type")
            )

            The default key is optional.

            If self.type is:
                * list, the OrderedDict will contains the key items
                * tuple, he OrderedDict will contains the key symbols
                * dict, he OrderedDict will contains the key values
        """
        template = OrderedDict([
            ("name", self.name),
            ("type", self.to_avro_type),
        ])

        default = self.get_default_value()
        if default is not None:
            template["default"] = default

        if self.items_type:
            template["items"] = self.items_type
        elif self.values_type:
            template["values"] = self.values_type
        elif self.symbols:
            template["symbols"] = self.symbols

        return template

    def to_json(self) -> str:
        return json.dumps(self.render())

    def to_dict(self) -> dict:
        return json.loads(self.to_json())
