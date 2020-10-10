import abc
import collections
import dataclasses
import datetime
import json
import random
import typing
import uuid
from collections import OrderedDict

import inflect
from faker import Faker
from pytz import utc

from dataclasses_avroschema import types, utils

fake = Faker()
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
FIXED = "fixed"
DATE = "date"
TIME_MILLIS = "time-millis"
TIMESTAMP_MILLIS = "timestamp-millis"
UUID = "uuid"
LOGICAL_DATE = {"type": INT, "logicalType": DATE}
LOGICAL_TIME = {"type": INT, "logicalType": TIME_MILLIS}
LOGICAL_DATETIME = {"type": LONG, "logicalType": TIMESTAMP_MILLIS}
LOGICAL_UUID = {"type": STRING, "logicalType": UUID}

PYTHON_TYPE_TO_AVRO = {
    bool: BOOLEAN,
    type(None): NULL,
    int: INT,
    float: FLOAT,
    bytes: BYTES,
    str: STRING,
    list: {"type": ARRAY},
    tuple: {"type": ARRAY},
    dict: {"type": MAP},
    types.Fixed: {"type": FIXED},
    types.Enum: {"type": ENUM},
    datetime.date: {"type": INT, "logicalType": DATE},
    datetime.time: {"type": INT, "logicalType": TIME_MILLIS},
    datetime.datetime: {"type": LONG, "logicalType": TIMESTAMP_MILLIS},
    uuid.uuid4: {"type": STRING, "logicalType": UUID},
}

# excluding tuple because is a container
PYTHON_INMUTABLE_TYPES = (str, int, bool, float, bytes, type(None))

PYTHON_PRIMITIVE_CONTAINERS = (list, tuple, dict)

PYTHON_LOGICAL_TYPES = (
    datetime.date,
    datetime.time,
    datetime.datetime,
    uuid.uuid4,
    uuid.UUID,
)

PYTHON_PRIMITIVE_TYPES = PYTHON_INMUTABLE_TYPES + PYTHON_PRIMITIVE_CONTAINERS

PRIMITIVE_AND_LOGICAL_TYPES = PYTHON_INMUTABLE_TYPES + PYTHON_LOGICAL_TYPES

PythonImnutableTypes = typing.Union[
    str, int, bool, float, list, tuple, dict, datetime.date, datetime.time, datetime.datetime, uuid.UUID
]


@dataclasses.dataclass  # type: ignore
class BaseField:
    avro_type: typing.ClassVar

    name: str
    type: typing.Any  # store the python primitive type
    default: typing.Any
    metadata: typing.Mapping = dataclasses.field(default_factory=dict)

    @staticmethod
    def _get_self_reference_type(a_type: typing.Any) -> str:
        internal_type = a_type.__args__[0]

        return internal_type.__forward_arg__

    @staticmethod
    def get_singular_name(name: str) -> str:
        singular = p.singular_noun(name)

        if singular:
            return singular
        return name

    def get_metadata(self) -> typing.List[typing.Tuple[str, str]]:
        meta_data_for_template = []
        try:
            metadata = dict(self.metadata)
            for name, value in metadata.items():
                meta_data_for_template.append((name, value))
        except (ValueError, TypeError):
            return meta_data_for_template
        return meta_data_for_template

    def render(self) -> OrderedDict:
        """
        Render the fields base on the avro field

        At least will have name and type.

        returns:
            OrderedDict(
                ("name", "a name"),
                ("type", "a type"),
                ("default", "default value")
            )

            The default key is optional.

            If self.type is:
                * list, the OrderedDict will contains the key items inside type
                * tuple, he OrderedDict will contains the key symbols inside type
                * dict, he OrderedDict will contains the key values inside type
        """
        template = OrderedDict([("name", self.name), ("type", self.get_avro_type())] + self.get_metadata())

        default = self.get_default_value()
        if default is not dataclasses.MISSING:
            template["default"] = default

        return template

    def get_default_value(self) -> typing.Any:
        if self.default in (dataclasses.MISSING, None):
            return self.default
        else:
            self.validate_default()
            return self.default

    def validate_default(self) -> bool:
        msg = f"Invalid default type. Default should be {self.type}"
        assert isinstance(self.default, self.type), msg

        return True

    def to_json(self) -> str:
        return json.dumps(self.render(), indent=2)

    def to_dict(self) -> dict:
        return json.loads(self.to_json())

    @abc.abstractmethod
    def get_avro_type(self) -> typing.Any:
        ...  # pragma: no cover

    def fake(self) -> typing.Any:
        return None


class InmutableField(BaseField):
    def get_avro_type(self) -> PythonImnutableTypes:
        if self.default is None:
            return [NULL, self.avro_type]
        return self.avro_type


@dataclasses.dataclass
class StringField(InmutableField):
    avro_type: typing.ClassVar = STRING

    def fake(self) -> str:
        return fake.pystr()


@dataclasses.dataclass
class IntegerField(InmutableField):
    avro_type: typing.ClassVar = INT

    def fake(self) -> int:
        return fake.pyint()


@dataclasses.dataclass
class BooleanField(InmutableField):
    avro_type: typing.ClassVar = BOOLEAN

    def fake(self) -> bool:
        return fake.pybool()


@dataclasses.dataclass
class FloatField(InmutableField):
    avro_type: typing.ClassVar = FLOAT

    def fake(self) -> float:
        return fake.pyfloat()


@dataclasses.dataclass
class BytesField(InmutableField):
    avro_type: typing.ClassVar = BYTES

    def get_default_value(self) -> typing.Any:
        if self.default in (dataclasses.MISSING, None):
            return self.default
        else:
            self.validate_default()
            return self.to_avro(self.default)

    @staticmethod
    def to_avro(item: bytes) -> str:
        return item.decode()

    def fake(self) -> bytes:
        return fake.pystr().encode()


@dataclasses.dataclass
class NoneField(InmutableField):
    avro_type: typing.ClassVar = NULL


@dataclasses.dataclass
class ContainerField(BaseField):
    default_factory: typing.Optional[typing.Callable] = None

    def get_avro_type(self) -> PythonImnutableTypes:
        avro_type = self.avro_type
        avro_type["name"] = self.get_singular_name(self.name)

        return avro_type


@dataclasses.dataclass
class ListField(ContainerField):
    items_type: typing.Any = None
    internal_field: typing.Any = None

    def __post_init__(self) -> None:
        self.generate_items_type()

    @property
    def avro_type(self) -> typing.Dict:
        return {"type": ARRAY, "items": self.items_type}

    def get_default_value(self) -> typing.Union[typing.List, dataclasses._MISSING_TYPE]:
        if self.default is None:
            return []
        elif callable(self.default_factory):
            # expecting a callable
            default = self.default_factory()
            assert isinstance(default, list), f"List is required as default for field {self.name}"

            clean_items = []
            for item in default:
                item_type = type(item)
                if item_type in LOGICAL_CLASSES:
                    clean_item = LOGICAL_TYPES_FIELDS_CLASSES[item_type].to_avro(item)  # type: ignore
                else:
                    clean_item = item
                clean_items.append(clean_item)

            return clean_items
        return dataclasses.MISSING

    def generate_items_type(self) -> typing.Any:
        # because avro can have only one type, we take the first one
        items_type = self.type.__args__[0]
        name = self.get_singular_name(self.name)

        if utils.is_union(items_type):
            self.items_type = UnionField(
                name, items_type, default=self.default, default_factory=self.default_factory
            ).get_avro_type()
        else:
            self.internal_field = AvroField(name, items_type)
            self.items_type = self.internal_field.get_avro_type()

    def fake(self) -> typing.List:
        # return a list of one element with the type specified
        return [self.internal_field.fake()]


@dataclasses.dataclass
class DictField(ContainerField):
    values_type: typing.Any = None
    internal_field: typing.Any = None

    def __post_init__(self) -> None:
        self.generate_values_type()

    @property
    def avro_type(self) -> typing.Dict[str, typing.Any]:
        return {"type": MAP, "values": self.values_type}

    def get_default_value(self) -> typing.Union[typing.Dict[str, typing.Any], dataclasses._MISSING_TYPE]:
        if self.default is None:
            return {}
        elif callable(self.default_factory):
            # expeting a callable
            default = self.default_factory()
            assert isinstance(default, dict), f"Dict is required as default for field {self.name}"

            clean_items = {}
            for key, value in default.items():
                value_type = type(value)
                if value_type in LOGICAL_CLASSES:
                    clean_item = LOGICAL_TYPES_FIELDS_CLASSES[value_type].to_avro(value)  # type: ignore
                else:
                    clean_item = value
                clean_items[key] = clean_item

            return clean_items
        return dataclasses.MISSING

    def generate_values_type(self) -> typing.Any:
        """
        Process typing.Dict. Avro assumes that the key of a map is always a string,
        so we take the second argument to determine the value type
        """
        values_type = self.type.__args__[1]

        name = self.get_singular_name(self.name)
        self.internal_field = AvroField(name, values_type)
        self.values_type = self.internal_field.get_avro_type()

    def fake(self) -> typing.Dict[str, typing.Any]:
        # return a dict of one element with the items type specified
        return {fake.pystr(): self.internal_field.fake()}


@dataclasses.dataclass
class UnionField(BaseField):
    default_factory: typing.Optional[typing.Callable] = None
    unions: typing.List = dataclasses.field(default_factory=list)
    internal_fields: typing.List = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        self.unions = self.generate_unions_type()

    def generate_unions_type(self) -> typing.List:
        """
        Generate union.

        Arguments:
            elements (typing.List): List of python types
            default (typing.Any): Default value
            default factory (typing.Calleable): Callable to get the default value for
                a list or dict type

        Returns:
            typing.List: List of avro types
        """
        elements = self.type.__args__
        name = self.get_singular_name(self.name)

        unions = []
        for element in elements:
            # create the field and get the avro type
            field = AvroField(name, element)
            unions.append(field.get_avro_type())
            self.internal_fields.append(field)

        if self.default is None and self.default_factory is dataclasses.MISSING and NULL not in unions:
            unions.insert(0, NULL)

        return unions

    def get_avro_type(self) -> typing.List:
        return self.unions

    def get_default_value(self) -> typing.Any:
        is_default_factory_callable = callable(self.default_factory)

        if self.default in (dataclasses.MISSING, None) and not is_default_factory_callable:
            return self.default
        elif is_default_factory_callable:
            # expeting a callable
            default = self.default_factory()  # type: ignore
            assert isinstance(default, (dict, list)), f"Dict or List is required as default for field {self.name}"

            return default
        elif type(self.default) in LOGICAL_CLASSES:
            return LOGICAL_TYPES_FIELDS_CLASSES[type(self.default)].to_avro(self.default)  # type: ignore
        return self.default

    def fake(self) -> typing.Any:
        # get a random internal field and return a fake value
        field = random.choice(self.internal_fields)
        return field.fake()


@dataclasses.dataclass
class FixedField(BaseField):
    def get_avro_type(self) -> typing.Dict[str, typing.Any]:
        avro_type = {
            "type": FIXED,
            "name": self.get_singular_name(self.name),
            "size": int(self.default.size),
        }

        if self.default.namespace is not None:
            avro_type["namespace"] = self.default.namespace

        if self.default.aliases is not None:
            avro_type["aliases"] = self.default.aliases

        return avro_type

    def get_default_value(self) -> dataclasses._MISSING_TYPE:
        return dataclasses.MISSING

    def fake(self) -> bytes:
        return fake.pystr(max_chars=self.default.size).encode()


@dataclasses.dataclass
class EnumField(BaseField):
    def get_avro_type(self) -> typing.Dict[str, typing.Any]:
        avro_type = {
            "type": ENUM,
            "name": self.get_singular_name(self.name),
            "symbols": self.default.symbols,
        }

        if self.default.namespace is not None:
            avro_type["namespace"] = self.default.namespace

        if self.default.aliases is not None:
            avro_type["aliases"] = self.default.aliases

        return avro_type

    def get_default_value(self) -> typing.Union[str, dataclasses._MISSING_TYPE, None]:
        default = self.default.default

        if default == types.MissingSentinel:
            return dataclasses.MISSING
        elif default in (dataclasses.MISSING, None):
            return default
        else:
            # check that the default value is listed in symbols
            assert (
                default in self.default.symbols
            ), f"The default value should be on of {self.default.symbols}. Current is {default}"
            return default

    def fake(self) -> typing.Any:
        return random.choice(self.default.symbols)


@dataclasses.dataclass
class SelfReferenceField(BaseField):
    def get_avro_type(self) -> typing.Union[typing.List[str], str]:
        str_type = self._get_self_reference_type(self.type)

        if self.default is None:
            # means that default value is None
            return [NULL, str_type]
        return str_type

    def get_default_value(self) -> typing.Union[dataclasses._MISSING_TYPE, None]:
        # Only check for None because self reference default value can be only None
        if self.default is None:
            return None
        return dataclasses.MISSING


class LogicalTypeField(InmutableField):
    def get_default_value(self) -> typing.Union[None, str, int, float]:
        if self.default in (dataclasses.MISSING, None):
            return self.default
        else:
            self.validate_default()
            # Convert to datetime and get the amount of days
            return self.to_avro(self.default)

    @staticmethod
    def to_avro(value: typing.Any) -> typing.Union[int, float, str]:
        ...  # type: ignore  # pragma: no cover


@dataclasses.dataclass
class DateField(LogicalTypeField):
    """
    The date logical type represents a date within the calendar,
    with no reference to a particular time zone or time of day.

    A date logical type annotates an Avro int, where the int stores
    the number of days from the unix epoch, 1 January 1970 (ISO calendar).
    """

    avro_type: typing.ClassVar = LOGICAL_DATE

    @staticmethod
    def to_avro(date: datetime.date) -> int:
        """
        Convert to datetime and get the amount of days
        from the unix epoch, 1 January 1970 (ISO calendar)
        for a given date

        Arguments:
            date (datetime.date)

        Returns:
            int
        """
        date_time = datetime.datetime.combine(date, datetime.datetime.min.time())
        ts = (date_time - utils.epoch_naive).total_seconds()

        return int(ts / (3600 * 24))

    def fake(self) -> datetime.date:
        return fake.date_object()


@dataclasses.dataclass
class TimeField(LogicalTypeField):
    """
    The time-millis logical type represents a time of day,
    with no reference to a particular calendar,
    time zone or date, with a precision of one millisecond.

    A time-millis logical type annotates an Avro int,
    where the int stores the number of milliseconds after midnight, 00:00:00.000.
    """

    avro_type: typing.ClassVar = LOGICAL_TIME

    @staticmethod
    def to_avro(time: datetime.time) -> int:
        """
        Returns the number of milliseconds after midnight, 00:00:00.000
        for a given time object

        Arguments:
            time (datetime.time)

        Returns:
            int
        """
        hour, minutes, seconds, microseconds = (
            time.hour,
            time.minute,
            time.second,
            time.microsecond,
        )

        return int((((hour * 60 + minutes) * 60 + seconds) * 1000) + (microseconds / 1000))

    def fake(self) -> datetime.time:
        return fake.time_object()


@dataclasses.dataclass
class DatetimeField(LogicalTypeField):
    """
    The timestamp-millis logical type represents an instant on the global timeline,
    independent of a particular time zone or calendar, with a precision of one millisecond.

    A timestamp-millis logical type annotates an Avro long,
    where the long stores the number of milliseconds from the unix epoch,
    1 January 1970 00:00:00.000 UTC.
    """

    avro_type: typing.ClassVar = LOGICAL_DATETIME

    @staticmethod
    def to_avro(date_time: datetime.datetime) -> float:
        """
        Returns the number of milliseconds from the unix epoch,
        1 January 1970 00:00:00.000 UTC for a given datetime

        Arguments:
            date_time (datetime.datetime)

        Returns:
            float
        """
        if date_time.tzinfo:
            ts = (date_time - utils.epoch).total_seconds()
        else:
            ts = (date_time - utils.epoch_naive).total_seconds()

        return ts * 1000

    def fake(self) -> datetime.datetime:
        return fake.date_time(tzinfo=utc)


@dataclasses.dataclass
class UUIDField(LogicalTypeField):
    avro_type: typing.ClassVar = LOGICAL_UUID

    def validate_default(self) -> bool:
        msg = f"Invalid default type. Default should be {str} or {uuid.UUID}"
        assert isinstance(self.default, (str, uuid.UUID)), msg

        return True

    @staticmethod
    def to_avro(uuid: uuid.UUID) -> str:
        return str(uuid)

    def fake(self) -> uuid.UUID:
        return uuid.uuid4()


@dataclasses.dataclass
class RecordField(BaseField):
    def get_avro_type(self) -> typing.Union[typing.List, typing.Dict]:
        record_type = self.type.avro_schema_to_python()

        # when there is a nested record replace its name
        # to avoid name colisions
        record_name = self.type.__name__.lower()
        if record_name not in self.name:
            name = f"{self.name}_{record_name}_record"
        else:
            name = f"{self.name}_record"

        record_type["name"] = name

        if self.default is None:
            return [NULL, record_type]
        return record_type

    def fake(self) -> typing.Any:
        return self.type.fake()


INMUTABLE_FIELDS_CLASSES = {
    bool: BooleanField,
    int: IntegerField,
    float: FloatField,
    bytes: BytesField,
    str: StringField,
    type(None): NoneField,
}

CONTAINER_FIELDS_CLASSES = {
    tuple: ListField,
    list: ListField,
    collections.abc.Sequence: ListField,
    collections.abc.MutableSequence: ListField,
    dict: DictField,
    collections.abc.Mapping: DictField,
    collections.abc.MutableMapping: DictField,
    typing.Union: UnionField,
}

LOGICAL_TYPES_FIELDS_CLASSES = {
    datetime.date: DateField,
    datetime.time: TimeField,
    datetime.datetime: DatetimeField,
    uuid.uuid4: UUIDField,
    uuid.UUID: UUIDField,
    bytes: BytesField,
}

PRIMITIVE_LOGICAL_TYPES_FIELDS_CLASSES = {
    **INMUTABLE_FIELDS_CLASSES,
    **LOGICAL_TYPES_FIELDS_CLASSES,  # type: ignore
    types.Fixed: FixedField,
    types.Enum: EnumField,
}

LOGICAL_CLASSES = LOGICAL_TYPES_FIELDS_CLASSES.keys()

FieldType = typing.Union[
    StringField,
    BooleanField,
    FloatField,
    BytesField,
    NoneField,
    ListField,
    DictField,
    UnionField,
    FixedField,
    EnumField,
    SelfReferenceField,
    DateField,
    TimeField,
    DatetimeField,
    UUIDField,
    RecordField,
    InmutableField,
]


def field_factory(
    name: str,
    native_type: typing.Any,
    default: typing.Any = dataclasses.MISSING,
    default_factory: typing.Any = dataclasses.MISSING,
    metadata: typing.Mapping = dataclasses.field(default_factory=dict),
) -> FieldType:
    if native_type in PYTHON_INMUTABLE_TYPES:
        klass = INMUTABLE_FIELDS_CLASSES[native_type]
        return klass(name=name, type=native_type, default=default, metadata=metadata)
    elif utils.is_self_referenced(native_type):
        return SelfReferenceField(name=name, type=native_type, default=default, metadata=metadata)
    elif native_type is types.Fixed:
        return FixedField(name=name, type=native_type, default=default, metadata=metadata)
    elif native_type is types.Enum:
        return EnumField(name=name, type=native_type, default=default, metadata=metadata)
    elif isinstance(native_type, typing._GenericAlias):  # type: ignore
        origin = native_type.__origin__

        if origin not in (
            tuple,
            list,
            dict,
            typing.Union,
            collections.abc.Sequence,
            collections.abc.MutableSequence,
            collections.abc.Mapping,
            collections.abc.MutableMapping,
        ):
            raise ValueError(
                f"""
                Invalid Type for field {name}. Accepted types are list, tuple, dict or typing.Union
                """
            )

        container_klass = CONTAINER_FIELDS_CLASSES[origin]
        return container_klass(  # type: ignore
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            default_factory=default_factory,
        )
    elif native_type in PYTHON_LOGICAL_TYPES:
        klass = LOGICAL_TYPES_FIELDS_CLASSES[native_type]
        return klass(name=name, type=native_type, default=default, metadata=metadata)
    else:
        return RecordField(name=name, type=native_type, default=default, metadata=metadata)


AvroField = field_factory
