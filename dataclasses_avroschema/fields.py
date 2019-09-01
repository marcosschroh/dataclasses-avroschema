import json
import dataclasses
import typing

from collections import OrderedDict


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
    list: {"type": ARRAY},
    tuple: {"type": ENUM},
    dict: {"type": MAP},
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
    default_factory: typing.Any = None

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
                self.items_type = PYTHON_TYPE_TO_AVRO[self.type.__args__[0]]
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

    def get_avro_type(self) -> PythonPrimitiveTypes:
        avro_type = PYTHON_TYPE_TO_AVRO.get(self.type)

        if self.type in PYTHON_INMUTABLE_TYPES:
            if self.default is not dataclasses.MISSING and self.type is not tuple:
                if self.default is not None:
                    return [avro_type, NULL]
                # means that default value is None
                return [NULL, avro_type]

            return avro_type
        elif self.type in PYTHON_PRIMITIVE_CONTAINERS:
            if self.items_type:
                avro_type["items"] = self.items_type
            elif self.values_type:
                avro_type["values"] = self.values_type
            elif self.symbols:
                avro_type["symbols"] = self.symbols

            avro_type["name"] = self.name
            return avro_type
        else:
            # we need to see what to to when is a custom type
            pass

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.type in PYTHON_INMUTABLE_TYPES:
                if self.default is None:
                    return NULL
                return self.default
            elif self.type is list:
                if self.default is None:
                    return []
            elif self.type is dict:
                if self.default is None:
                    return {}
        elif self.default_factory not in (dataclasses.MISSING, None):
            if self.type is list:
                # expeting a callable
                default = self.default_factory()
                assert isinstance(default, list), f"List is required as default for field {self.name}"

                print(default)
                return default
            elif self.type is dict:
                # expeting a callable
                default = self.default_factory()
                assert isinstance(default, dict), f"Dict is required as default for field {self.name}"

                return default

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
                * list, the OrderedDict will contains the key items inside type
                * tuple, he OrderedDict will contains the key symbols inside type
                * dict, he OrderedDict will contains the key values inside type
        """
        template = OrderedDict([
            ("name", self.name),
            ("type", self.get_avro_type()),
        ])

        default = self.get_default_value()
        if default is not None:
            template["default"] = default

        return template

    def to_json(self) -> str:
        return json.dumps(self.render())

    def to_dict(self) -> dict:
        return json.loads(self.to_json())
