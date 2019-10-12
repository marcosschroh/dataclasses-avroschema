import json
import dataclasses
import typing
import inflect
import datetime
import uuid

from collections import OrderedDict

from dataclasses_avroschema import schema_generator

p = inflect.engine()

BOOLEAN = "boolean"
NULL = "null"
INT = "int"
FLOAT = "float"
LONG = "long"
BYTES = "bytes"
STRING = "string"
ARRAY = "array"
ENUM = "enum"
MAP = "map"
DATE = "date"
TIME_MILLIS = "time-millis"
TIMESTAMP_MILLIS = "timestamp-millis"
UUID = "uuid"


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
    datetime.date: {"type": INT, "logicalType": DATE},
    datetime.time: {"type": INT, "logicalType": TIME_MILLIS},
    datetime.datetime: {"type": LONG, "logicalType": TIMESTAMP_MILLIS},
    uuid.uuid4: {'type': 'string', 'logicalType': UUID}
}

# excluding tuple because is a container
PYTHON_INMUTABLE_TYPES = (str, int, bool, float, bytes)

PYTHON_PRIMITIVE_CONTAINERS = (list, tuple, dict)

PYTHON_LOGICAL_TYPES = (datetime.date, datetime.time, datetime.datetime, uuid.uuid4)

PYTHON_PRIMITIVE_TYPES = PYTHON_INMUTABLE_TYPES + PYTHON_PRIMITIVE_CONTAINERS

PythonPrimitiveTypes = typing.Union[str, int, bool, float, list, tuple, dict]


@dataclasses.dataclass
class BaseField:
    name: str
    type: typing.Any  # store the python type (Field)
    default: typing.Any = dataclasses.MISSING

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

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.default is None:
                return NULL
            return self.default

    def to_json(self) -> str:
        return json.dumps(self.render())

    def to_dict(self) -> dict:
        return json.loads(self.to_json())


class InmutableField(BaseField):

    def get_avro_type(self) -> PythonPrimitiveTypes:
        if self.default is not dataclasses.MISSING:
            if self.default is not None:
                return [self.avro_type, NULL]
            # means that default value is None
            return [NULL, self.avro_type]

        return self.avro_type


@dataclasses.dataclass
class StringField(InmutableField):
    avro_type: typing.ClassVar = STRING


@dataclasses.dataclass
class IntegerField(InmutableField):
    avro_type: typing.ClassVar = INT


@dataclasses.dataclass
class BooleanField(InmutableField):
    avro_type: typing.ClassVar = BOOLEAN


@dataclasses.dataclass
class FloatField(InmutableField):
    avro_type: typing.ClassVar = FLOAT


@dataclasses.dataclass
class BytesField(InmutableField):
    avro_type: typing.ClassVar = BYTES


@dataclasses.dataclass
class TupleField(BaseField):
    avro_type: typing.ClassVar = ENUM
    symbols: typing.Any = None
    default_factory: typing.Any = None

    def __post_init__(self):
        self.generate_symbols()

    def get_avro_type(self) -> PythonPrimitiveTypes:
        avro_type = {
            "type": ENUM,
            "symbols": self.symbols
        }

        avro_type["name"] = self.get_singular_name(self.name)
        return avro_type

    def get_default_value(self):
        return

    def generate_symbols(self):
        self.symbols = list(self.default)


@dataclasses.dataclass
class ListField(BaseField):
    avro_type: typing.ClassVar = ARRAY
    items_type: typing.Any = None
    default_factory: typing.Any = None

    def __post_init__(self):
        self.generate_items_type()

    def get_avro_type(self) -> PythonPrimitiveTypes:
        avro_type = {
            "type": ARRAY,
            "items": self.items_type
        }

        avro_type["name"] = self.get_singular_name(self.name)
        return avro_type

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.default is None:
                return []
        elif self.default_factory not in (dataclasses.MISSING, None):
            # expeting a callable
            default = self.default_factory()
            assert isinstance(default, list), f"List is required as default for field {self.name}"

            return default

    def generate_items_type(self):
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


@dataclasses.dataclass
class DictField(BaseField):
    avro_type: typing.ClassVar = MAP
    default_factory: typing.Any = None
    values_type: typing.Any = None

    def __post_init__(self):
        self.generate_values_type()

    def get_avro_type(self) -> PythonPrimitiveTypes:
        avro_type = {
            "type": MAP,
            "values": self.values_type
        }

        avro_type["name"] = self.get_singular_name(self.name)
        return avro_type

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.default is None:
                return {}
        elif self.default_factory not in (dataclasses.MISSING, None):
            # expeting a callable
            default = self.default_factory()
            assert isinstance(default, dict), f"Dict is required as default for field {self.name}"

            return default

    def generate_values_type(self):
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


@dataclasses.dataclass
class SelfReferenceField(BaseField):

    def get_avro_type(self):
        return self._get_self_reference_type(self.type)

    def get_default_value(self):
        return


@dataclasses.dataclass
class DateField(BaseField):
    """
    The date logical type represents a date within the calendar,
    with no reference to a particular time zone or time of day.

    A date logical type annotates an Avro int, where the int stores
    the number of days from the unix epoch, 1 January 1970 (ISO calendar).
    """
    avro_type: typing.ClassVar = DATE

    def get_avro_type(self):
        return {"type": INT, "logicalType": self.avro_type}

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.default is None:
                return NULL

            # Convert to datetime and get the amount of days
            date_time = datetime.datetime.combine(self.default, datetime.datetime.min.time())
            ts = (date_time - datetime.datetime(1970, 1, 1)).total_seconds()
            return int(ts / (3600 * 24))


@dataclasses.dataclass
class TimeField(BaseField):
    """
    The time-millis logical type represents a time of day,
    with no reference to a particular calendar,
    time zone or date, with a precision of one millisecond.

    A time-millis logical type annotates an Avro int,
    where the int stores the number of milliseconds after midnight, 00:00:00.000.
    """
    avro_type: typing.ClassVar = TIME_MILLIS

    def get_avro_type(self):
        return {"type": INT, "logicalType": self.avro_type}

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.default is None:
                return NULL

            return self.time_to_miliseconds(self.default)

    @staticmethod
    def time_to_miliseconds(time):
        hour, minutes, seconds, microseconds = time.hour, time.minute, time.second, time.microsecond

        return int((((hour * 60 + minutes) * 60 + seconds) * 1000) + (microseconds / 1000))


@dataclasses.dataclass
class DatetimeField(BaseField):
    """
    The timestamp-millis logical type represents an instant on the global timeline,
    independent of a particular time zone or calendar, with a precision of one millisecond.

    A timestamp-millis logical type annotates an Avro long,
    where the long stores the number of milliseconds from the unix epoch,
    1 January 1970 00:00:00.000 UTC.
    """
    avro_type: typing.ClassVar = TIMESTAMP_MILLIS

    def get_avro_type(self):
        return {"type": LONG, "logicalType": self.avro_type}

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.default is None:
                return NULL

            ts = (self.default - datetime.datetime(1970, 1, 1)).total_seconds()
            return ts * 1000


@dataclasses.dataclass
class UUIDField(BaseField):
    avro_type: typing.ClassVar = UUID

    def get_avro_type(self):
        return {'type': 'string', 'logicalType': self.avro_type}

    def get_default_value(self):
        if self.default is not dataclasses.MISSING:
            if self.default is None:
                return NULL

            return str(self.default)


@dataclasses.dataclass
class RecordField(BaseField):

    def get_avro_type(self):
        return schema_generator.SchemaGenerator(self.type).avro_schema_to_python()


INMUTABLE_FIELDS_CLASSES = {
    bool: BooleanField,
    int: IntegerField,
    float: FloatField,
    bytes: BytesField,
    str: StringField,
}

CONTAINER_FIELDS_CLASSES = {
    tuple: TupleField,
    list: ListField,
    dict: DictField,
}

LOGICAL_TYPES_FIELDS_CLASSES = {
    datetime.date: DateField,
    datetime.time: TimeField,
    datetime.datetime: DatetimeField,
    uuid.uuid4: UUIDField
}


def field_factory(name: str, native_type: typing.Any, default: typing.Any = dataclasses.MISSING,
                  default_factory: typing.Any = None):

    if native_type in PYTHON_INMUTABLE_TYPES:
        klass = INMUTABLE_FIELDS_CLASSES[native_type]
        return klass(name=name, type=native_type, default=default)
    elif BaseField.is_self_referenced(native_type):
        return SelfReferenceField(name=name, type=native_type, default=default)
    elif isinstance(native_type, typing._GenericAlias):
        origin = native_type.__origin__

        if origin not in (tuple, list, dict):
            raise ValueError(
                f"Invalid Type for field {name}. Accepted types are list, tuple or dict")

        klass = CONTAINER_FIELDS_CLASSES[origin]
        return klass(name=name, type=native_type, default=default, default_factory=default_factory)
    elif native_type in PYTHON_LOGICAL_TYPES:
        klass = LOGICAL_TYPES_FIELDS_CLASSES[native_type]
        return klass(name=name, type=native_type, default=default)
    else:
        return RecordField(name=name, type=native_type, default=default)


Field = field_factory
