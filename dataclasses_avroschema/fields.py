import abc
import collections
import dataclasses
import datetime
import decimal
import enum
import inspect
import json
import logging
import random
import sys
import typing
import uuid
from collections import OrderedDict

import inflect
from faker import Faker
from pytz import utc

from dataclasses_avroschema import schema_generator, serialization, types, utils

from . import field_utils
from .exceptions import InvalidMap, NameSpaceRequiredException
from .types import JsonDict

PY_VER = sys.version_info

if PY_VER >= (3, 9):  # pragma: no cover
    GenericAlias = (typing.GenericAlias, typing._GenericAlias, typing._SpecialGenericAlias, typing._UnionGenericAlias)  # type: ignore # noqa: E501
else:
    GenericAlias = typing._GenericAlias  # type: ignore  # pragma: no cover

logger = logging.getLogger(__name__)

fake = Faker()
p = inflect.engine()


@dataclasses.dataclass  # type: ignore
class BaseField:
    __slots__ = (
        "name",
        "type",
        "default",
        "parent",
    )

    name: str
    type: typing.Any  # store the python primitive type
    default: typing.Any
    parent: typing.Any
    metadata: typing.Optional[typing.Mapping] = None
    model_metadata: typing.Optional[utils.SchemaMetadata] = None

    def __post_init__(self) -> None:
        self.model_metadata = self.model_metadata or utils.SchemaMetadata()  # type: ignore

    @property
    def avro_type(self) -> typing.Union[str, typing.Dict]:
        ...  # pragma: no cover

    @staticmethod
    def _get_self_reference_type(a_type: typing.Any) -> str:
        internal_type = a_type.__args__[0]

        return internal_type.__forward_arg__

    @staticmethod
    def get_singular_name(name: str) -> str:
        singular = p.singular_noun(name)

        # do the check because of mypy.
        # p.singular_noun returns Union[str, bool]
        if isinstance(singular, str):
            return singular
        return name

    def get_metadata(self) -> typing.List[typing.Tuple[str, str]]:
        meta_data_for_template = []

        if self.metadata is not None:
            try:
                for name, value in self.metadata.items():
                    meta_data_for_template.append((name, value))
            except (ValueError, TypeError):  # pragma: no cover
                logger.warn("Error during getting metadata")  # pragma: no cover
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
        template = OrderedDict(self.get_metadata() + [("name", self.name), ("type", self.get_avro_type())])

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
        if getattr(self.type, "__metadata__", [None])[0] in types.CUSTOM_TYPES:
            assert isinstance(self.default, self.type.__origin__)
        else:
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

    def exist_type(self) -> int:
        # filter by the same field types
        same_types = [
            field.type
            for field in self.parent.user_defined_types
            if field.type == self.type and field.name != self.name
        ]

        # If length > 0, means that it is the first appearance
        # of this type, otherwise exist already.
        return len(same_types)


class ImmutableField(BaseField):
    def get_avro_type(self) -> field_utils.PythonImmutableTypes:
        if self.default is None:
            return [field_utils.NULL, self.avro_type]
        return self.avro_type


@dataclasses.dataclass
class StringField(ImmutableField):
    avro_type: typing.ClassVar[str] = field_utils.STRING

    def fake(self) -> str:
        return fake.pystr()


@dataclasses.dataclass
class IntField(ImmutableField):
    avro_type: typing.ClassVar[str] = field_utils.INT

    def fake(self) -> int:
        return fake.pyint()


@dataclasses.dataclass
class LongField(ImmutableField):
    avro_type: typing.ClassVar[str] = field_utils.LONG

    def fake(self) -> int:
        return fake.pyint()


@dataclasses.dataclass
class BooleanField(ImmutableField):
    avro_type: typing.ClassVar[str] = field_utils.BOOLEAN

    def fake(self) -> bool:
        return fake.pybool()


@dataclasses.dataclass
class DoubleField(ImmutableField):
    avro_type: typing.ClassVar[str] = field_utils.DOUBLE

    def fake(self) -> float:
        return fake.pyfloat()


@dataclasses.dataclass
class FloatField(ImmutableField):
    avro_type: typing.ClassVar[str] = field_utils.FLOAT

    def fake(self) -> float:
        return fake.pyfloat()  # Roughly the range on a float32


@dataclasses.dataclass
class BytesField(ImmutableField):
    avro_type: typing.ClassVar[str] = field_utils.BYTES

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
class NoneField(ImmutableField):
    @property
    def avro_type(self) -> typing.Union[str, typing.Dict]:
        return field_utils.NULL


@dataclasses.dataclass
class ContainerField(BaseField):
    default_factory: typing.Optional[typing.Callable] = None

    @property
    def avro_type(self) -> typing.Dict:
        ...  # pragma: no cover

    def get_avro_type(self) -> field_utils.PythonImmutableTypes:
        avro_type = self.avro_type
        avro_type["name"] = self.get_singular_name(self.name)

        return avro_type


@dataclasses.dataclass
class ListField(ContainerField):
    items_type: typing.Any = None
    internal_field: typing.Any = None

    @property
    def avro_type(self) -> typing.Dict:
        self.generate_items_type()
        return {"type": field_utils.ARRAY, "items": self.items_type}

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

        if utils.is_union(items_type):
            self.internal_field = UnionField(
                self.name,
                items_type,
                default=self.default,
                default_factory=self.default_factory,
                model_metadata=self.model_metadata,
                parent=self.parent,
            )
        else:
            self.internal_field = AvroField(
                self.name, items_type, model_metadata=self.model_metadata, parent=self.parent
            )

        self.items_type = self.internal_field.get_avro_type()

    def fake(self) -> typing.List:
        return [self.internal_field.fake()]


@dataclasses.dataclass
class DictField(ContainerField):
    values_type: typing.Any = None
    internal_field: typing.Any = None

    def __post_init__(self) -> None:
        key_type = self.type.__args__[0]

        if key_type is not str:
            raise InvalidMap(self.name, key_type)

    @property
    def avro_type(self) -> JsonDict:
        self.generate_values_type()
        return {"type": field_utils.MAP, "values": self.values_type}

    def get_default_value(self) -> typing.Union[JsonDict, dataclasses._MISSING_TYPE]:
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
        self.internal_field = AvroField(self.name, values_type, model_metadata=self.model_metadata, parent=self.parent)
        self.values_type = self.internal_field.get_avro_type()

    def fake(self) -> typing.Dict[str, typing.Any]:
        # return a dict of one element with the items type specified
        return {fake.pystr(): self.internal_field.fake()}


@dataclasses.dataclass
class UnionField(BaseField):
    default_factory: typing.Optional[typing.Callable] = None
    unions: typing.List = dataclasses.field(default_factory=list)
    internal_fields: typing.List = dataclasses.field(default_factory=list)

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

        unions: typing.List = []

        # Place default at front of list
        default_type = None
        if self.default is None and self.default_factory is dataclasses.MISSING:
            unions.insert(0, field_utils.NULL)
        elif type(self.default) is not dataclasses._MISSING_TYPE:
            default_type = type(self.default)
            default_field = AvroField(name, default_type, model_metadata=self.model_metadata, parent=self.parent)
            unions.append(default_field.get_avro_type())
            self.internal_fields.append(default_field)

        for element in elements:
            # create the field and get the avro type
            field = AvroField(name, element, model_metadata=self.model_metadata, parent=self.parent)
            avro_type = field.get_avro_type()

            if avro_type not in unions:
                unions.append(avro_type)
                self.internal_fields.append(field)

        return unions

    def get_avro_type(self) -> typing.List:
        self.unions = self.generate_unions_type()
        return self.unions

    def get_default_value(self) -> typing.Any:
        is_default_factory_callable = callable(self.default_factory)

        if self.default in (dataclasses.MISSING, None) and not is_default_factory_callable:
            return self.default
        elif is_default_factory_callable:
            # expecting a callable
            default = self.default_factory()  # type: ignore
            assert isinstance(default, (dict, list)), f"Dict or List is required as default for field {self.name}"

            return default
        elif type(self.default) in LOGICAL_CLASSES:
            return LOGICAL_TYPES_FIELDS_CLASSES[type(self.default)].to_avro(self.default)  # type: ignore
        elif issubclass(type(self.default), enum.Enum):
            return self.default.value
        return self.default

    def fake(self) -> typing.Any:
        # get a random internal field and return a fake value
        field = random.choice(self.internal_fields)
        return field.fake()


@dataclasses.dataclass
class FixedField(BaseField):
    def get_avro_type(self) -> JsonDict:
        avro_type = {
            "type": field_utils.FIXED,
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
    def _get_meta_class_attributes(self) -> typing.Dict[str, typing.Any]:
        # get Enum members
        members = self.type.__members__
        meta = members.get("Meta")

        if meta:
            metadata = utils.FieldMetadata.create(meta.value)
            return metadata.to_dict()
        return {}

    def get_symbols(self) -> typing.List[str]:
        return [member.value for member in self.type if member.name != "Meta"]

    def get_avro_type(self) -> typing.Union[str, JsonDict]:
        metadata = self._get_meta_class_attributes()
        name = self.type.__name__

        if not self.exist_type():
            user_defined_type = utils.UserDefinedType(name=name, type=self.type)
            self.parent.user_defined_types.add(user_defined_type)
            return {
                "type": field_utils.ENUM,
                "name": name,
                "symbols": self.get_symbols(),
                **metadata,
            }
        else:
            namespace = metadata.get("namespace")
            if namespace is None:
                raise NameSpaceRequiredException(field_type=self.type, field_name=name)
            return f"{namespace}.{name}"

    def get_default_value(self) -> typing.Union[str, dataclasses._MISSING_TYPE, None]:
        if self.default == types.MissingSentinel:
            return dataclasses.MISSING
        elif self.default in (dataclasses.MISSING, None):
            return self.default
        else:
            # check that the default value is listed in symbols
            assert (
                self.default.value in self.get_symbols()
            ), f"The default value should be one of {self.get_symbols()}. Current is {self.default}"
            return self.default.value

    def fake(self) -> typing.Any:
        return random.choice(self.get_symbols())


@dataclasses.dataclass
class SelfReferenceField(BaseField):
    def get_avro_type(self) -> typing.Union[typing.List[str], str]:
        str_type = self._get_self_reference_type(self.type)

        if self.default is None:
            # means that default value is None
            return [field_utils.NULL, str_type]
        return str_type

    def get_default_value(self) -> typing.Union[dataclasses._MISSING_TYPE, None]:
        # Only check for None because self reference default value can be only None
        if self.default is None:
            return None
        return dataclasses.MISSING


class LogicalTypeField(ImmutableField):
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

    @property
    def avro_type(self) -> typing.Dict:
        return field_utils.LOGICAL_DATE

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
class TimeMilliField(LogicalTypeField):
    """
    The time-millis logical type represents a time of day,
    with no reference to a particular calendar,
    time zone or date, with a precision of one millisecond.

    A time-millis logical type annotates an Avro int,
    where the int stores the number of milliseconds after midnight, 00:00:00.000.
    """

    @property
    def avro_type(self) -> typing.Dict:
        return field_utils.LOGICAL_TIME_MILIS

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
class TimeMicroField(LogicalTypeField):
    """
    The time-micros logical type represents a time of day,
    with no reference to a particular calendar,
    time zone or date, with a precision of one millisecond.

    A time-micros logical type annotates an Avro long,
    where the int stores the number of milliseconds after midnight, 00:00:00.000000.
    """

    @property
    def avro_type(self) -> typing.Dict:
        return field_utils.LOGICAL_TIME_MICROS

    @staticmethod
    def to_avro(time: datetime.time) -> float:
        """
        Returns the number of microseconds after midnight, 00:00:00.000000
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

        return int((((hour * 60 + minutes) * 60 + seconds) * 1000000) + microseconds)

    def fake(self) -> datetime.time:
        datetime_object: datetime.datetime = fake.date_time(tzinfo=utc)
        datetime_object = datetime_object + datetime.timedelta(microseconds=random.randint(0, 999))
        return datetime_object.time()


@dataclasses.dataclass
class DatetimeField(LogicalTypeField):
    """
    The timestamp-millis logical type represents an instant on the global timeline,
    independent of a particular time zone or calendar, with a precision of one millisecond.

    A timestamp-millis logical type annotates an Avro long,
    where the long stores the number of milliseconds from the unix epoch,
    1 January 1970 00:00:00.000 UTC.
    """

    @property
    def avro_type(self) -> typing.Dict:
        return field_utils.LOGICAL_DATETIME_MILIS

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

        return int(ts * 1000)

    def fake(self) -> datetime.datetime:
        return fake.date_time(tzinfo=utc)


@dataclasses.dataclass
class DatetimeMicroField(LogicalTypeField):
    """
    The timestamp-millis logical type represents an instant on the global timeline,
    independent of a particular time zone or calendar, with a precision of one millisecond.

    A timestamp-millis logical type annotates an Avro long,
    where the long stores the number of milliseconds from the unix epoch,
    1 January 1970 00:00:00.000000 UTC.
    """

    @property
    def avro_type(self) -> typing.Dict:
        return field_utils.LOGICAL_DATETIME_MICROS

    @staticmethod
    def to_avro(date_time: datetime.datetime) -> float:
        """
        Returns the number of milliseconds from the unix epoch,
        1 January 1970 00:00:00.000000 UTC for a given datetime

        Arguments:
            date_time (datetime.datetime)

        Returns:
            float
        """
        if date_time.tzinfo:
            ts = (date_time - utils.epoch).total_seconds()
        else:
            ts = (date_time - utils.epoch_naive).total_seconds()

        return int(ts * 1000000)

    def fake(self) -> datetime.datetime:
        datetime_object: datetime.datetime = fake.date_time(tzinfo=utc)
        return datetime_object + datetime.timedelta(microseconds=random.randint(0, 999))


@dataclasses.dataclass
class UUIDField(LogicalTypeField):
    @property
    def avro_type(self) -> typing.Dict:
        return field_utils.LOGICAL_UUID

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
    def get_avro_type(self) -> typing.Union[str, typing.List, typing.Dict]:
        meta = getattr(self.type, "Meta", type)
        metadata = utils.SchemaMetadata.create(meta)

        alias = self.parent.metadata.get_alias_nested_items(self.name) or metadata.get_alias_nested_items(self.name)  # type: ignore  # noqa E501

        # The priority for the schema name
        # 1. Check if exists an alias_nested_items in parent class or Meta class of own model
        # 2. Check if the schema_name is present in the Meta class of own model
        # 3. Use the default class Name (self.type.__name__)
        name = alias or metadata.schema_name or self.type.__name__

        if not self.exist_type() or alias is not None:
            user_defined_type = utils.UserDefinedType(name=name, type=self.type)
            self.parent.user_defined_types.add(user_defined_type)

            record_type = self.type.avro_schema_to_python(parent=self.parent)
            record_type["name"] = name
        else:
            if metadata.namespace is None:
                raise NameSpaceRequiredException(field_type=self.type, field_name=self.name)
            record_type = f"{metadata.namespace}.{name}"

        if self.default is None:
            return [field_utils.NULL, record_type]
        return record_type

    def fake(self) -> typing.Any:
        return self.type.fake()


@dataclasses.dataclass
class DecimalField(BaseField):
    precision: int = -1
    scale: int = 0

    def __post_init__(self) -> None:
        self.set_precision_scale()

    def set_precision_scale(self) -> None:
        if self.default != types.MissingSentinel:
            if isinstance(self.default, decimal.Decimal):
                _, digits, scale = self.default.as_tuple()
                self.scale = int(scale) * -1  # Make scale positive, as that's what Avro expects
                # decimal.Context has a precision property
                # BUT the precision property is independent of the number of digits stored in the Decimal instance
                # # # FROM THE DOCS HERE https://docs.python.org/3/library/decimal.html
                #  The context precision does not affect how many digits are stored.
                #  That is determined exclusively by the number of digits in value.
                #  For example, Decimal('3.00000') records all five zeros even if the context precision is only three.
                # # #
                # Avro is concerned with *what form the number takes* and not with *handling errors in the Python env*
                # so we take the number of digits stored in the decimal as Avro precision
                self.precision = len(digits)
            elif isinstance(self.default, types.Decimal):
                self.scale = self.default.scale
                self.precision = self.default.precision
            else:
                raise ValueError("decimal.Decimal default types must be either decimal.Decimal or types.Decimal")
        else:
            raise ValueError(
                "decimal.Decimal default types must be specified to provide precision and scale,"
                " and must be either decimal.Decimal or types.Decimal"
            )

        # Validation on precision and scale per Avro schema
        if self.precision <= 0:
            raise ValueError("Precision must be a positive integer greater than zero")

        if self.scale < 0 or self.precision < self.scale:
            raise ValueError("Scale must be zero or a positive integer less than or equal to the precision.")

            # Just pull the precision from default context and default out scale
            # Not ideal
            #
            # self.precision = decimal.Context().prec

    def get_avro_type(self) -> typing.Union[JsonDict, typing.List[typing.Union[str, JsonDict]]]:
        avro_type = {
            "type": field_utils.BYTES,
            "logicalType": field_utils.DECIMAL,
            "precision": self.precision,
            "scale": self.scale,
        }
        if not isinstance(self.default, decimal.Decimal) and self.default.default is None:
            return ["null", avro_type]

        return avro_type

    def get_default_value(self) -> typing.Union[str, dataclasses._MISSING_TYPE, None]:
        default = self.default

        if isinstance(default, types.Decimal):
            default = default.default

        if default == types.MissingSentinel:
            return dataclasses.MISSING
        if default is None:
            return None

        return serialization.decimal_to_str(default, self.precision, self.scale)

    def fake(self) -> decimal.Decimal:
        return fake.pydecimal(right_digits=self.scale, left_digits=self.precision - self.scale)


INMUTABLE_FIELDS_CLASSES = {
    bool: BooleanField,
    int: LongField,
    types.Int32: IntField,
    float: DoubleField,
    types.Float32: FloatField,
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
    datetime.time: TimeMilliField,
    types.TimeMicro: TimeMicroField,
    datetime.datetime: DatetimeField,
    types.DateTimeMicro: DatetimeMicroField,
    uuid.uuid4: UUIDField,
    uuid.UUID: UUIDField,
    bytes: BytesField,
    decimal.Decimal: DecimalField,
}

PRIMITIVE_LOGICAL_TYPES_FIELDS_CLASSES = {
    **INMUTABLE_FIELDS_CLASSES,  # type: ignore
    **LOGICAL_TYPES_FIELDS_CLASSES,  # type: ignore
    types.Fixed: FixedField,
}

LOGICAL_CLASSES = LOGICAL_TYPES_FIELDS_CLASSES.keys()

FieldType = typing.Union[
    StringField,
    LongField,
    BooleanField,
    DoubleField,
    BytesField,
    NoneField,
    ListField,
    DictField,
    UnionField,
    FixedField,
    EnumField,
    SelfReferenceField,
    DateField,
    TimeMilliField,
    DatetimeField,
    UUIDField,
    RecordField,
    ImmutableField,
]


def field_factory(
    name: str,
    native_type: typing.Any,
    parent: typing.Any = None,
    *,
    default: typing.Any = dataclasses.MISSING,
    default_factory: typing.Any = dataclasses.MISSING,
    metadata: typing.Optional[typing.Mapping] = None,
    model_metadata: typing.Optional[utils.SchemaMetadata] = None,
) -> FieldType:
    if metadata is None:
        metadata = {}

    if native_type in field_utils.PYTHON_INMUTABLE_TYPES:
        klass = INMUTABLE_FIELDS_CLASSES[native_type]
        return klass(
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif utils.is_self_referenced(native_type):
        return SelfReferenceField(
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif native_type is types.Fixed:
        return FixedField(
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif native_type in field_utils.PYTHON_LOGICAL_TYPES:
        klass = LOGICAL_TYPES_FIELDS_CLASSES[native_type]  # type: ignore

        return klass(
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif isinstance(native_type, GenericAlias):  # type: ignore
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
        # check here
        return container_klass(  # type: ignore
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            default_factory=default_factory,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif inspect.isclass(native_type) and issubclass(native_type, enum.Enum):
        return EnumField(
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif types.UnionType is not None and isinstance(native_type, types.UnionType):
        # we need to check whether types.UnionType because it works only in
        # python 3.9 or importing __future__ in previous python versions
        # cases when a container is used, for example `typing.List[int] | str` in python is
        # translated to typing.Union[typing.List[int], str] so it won't reach this point
        return UnionField(
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            default_factory=default_factory,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif inspect.isclass(native_type) and issubclass(native_type, schema_generator.AvroModel):
        return RecordField(
            name=name,
            type=native_type,
            default=default,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    else:
        msg = (
            f"Type {native_type} is unknown. Please check the valid types at "
            "https://marcosschroh.github.io/dataclasses-avroschema/fields_specification/#avro-field-and-python-types-summary"  # noqa: E501
        )

        raise ValueError(msg)


AvroField = field_factory
