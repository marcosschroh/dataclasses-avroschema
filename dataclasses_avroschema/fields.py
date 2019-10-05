import json
import dataclasses
import typing
import inflect

from collections import OrderedDict

from dataclasses_avroschema import schema_generator

p = inflect.engine()

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
    type: typing.Any  # store the python type (Field)
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
        if isinstance(self.type, typing._GenericAlias) and not self.is_self_referenced(self.type):
            # Means that could be a list, tuple or dict
            origin = self.type.__origin__
            processor = self.get_processor(origin)
            processor()

            self.type = origin

    def get_processor(self, origin):
        """
        Get processor for a specific type.

        Supported: tuple, list, dict and typing.Type (custom types)
        """
        if origin is list:
            return self._process_list_type
        elif origin is dict:
            return self._process_dict_type
        elif origin is tuple:
            return self._process_tuple_type
        else:
            # we do not accept any other typing._GenericAlias like a set
            # we should raise an exception
            raise ValueError(
                f"Invalid Type for field {self.name}. Accepted types are list, tuple or dict")

    def _process_list_type(self):
        # because avro can have only one type, we take the first one
        items_type = self.type.__args__[0]

        if items_type in PYTHON_PRIMITIVE_TYPES:
            self.items_type = PYTHON_TYPE_TO_AVRO[items_type]
        elif self.is_self_referenced(items_type):
            # Checking for a self reference. Maybe is a typing.ForwardRef
            self.items_type = self._get_self_reference_type(items_type)
        else:
            # Is Avro Record Type
            self.items_type = schema_generator.SchemaGenerator(
                items_type).avro_schema_to_python()

    def _process_dict_type(self):
        """
        Process typing.Dict. Avro assumes that the key of a map is always a string,
        so we take the second argument to determine the value type
        """
        values_type = self.type.__args__[1]

        if values_type in PYTHON_PRIMITIVE_TYPES:
            self.values_type = PYTHON_TYPE_TO_AVRO[values_type]
        elif self.is_self_referenced(values_type):
            # Checking for a self reference. Maybe is a typing.ForwardRef
            self.values_type = self._get_self_reference_type(values_type)
        else:
            self.values_type = schema_generator.SchemaGenerator(
                values_type).avro_schema_to_python()

    def _process_tuple_type(self):
        self.symbols = list(self.default)

    @staticmethod
    def _get_self_reference_type(a_type):
        internal_type = a_type.__args__[0]

        return internal_type.__forward_arg__

    @staticmethod
    def is_self_referenced(a_type):
        return isinstance(a_type, typing._GenericAlias) \
            and a_type.__args__ and isinstance(a_type.__args__[0], typing.ForwardRef)

    @staticmethod
    def get_singular_name(name):
        singular = p.singular_noun(name)

        if singular:
            return singular
        return name

    def get_avro_type(self) -> PythonPrimitiveTypes:
        if self.is_self_referenced(self.type):
            return self._get_self_reference_type(self.type)

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

            avro_type["name"] = self.get_singular_name(self.name)
            return avro_type
        else:
            # Assuming that is a Avro Record type.
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
            elif self.type is dict:
                if self.default is None:
                    return {}
        elif self.default_factory not in (dataclasses.MISSING, None):
            if self.type is list:
                # expeting a callable
                default = self.default_factory()
                assert isinstance(default, list), f"List is required as default for field {self.name}"

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
