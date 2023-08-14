import collections
import dataclasses
import datetime
import decimal
import enum
import inspect
import random
import sys
import typing
import uuid

from typing_extensions import get_args, get_origin

from dataclasses_avroschema import schema_generator, serialization, types, utils
from dataclasses_avroschema.exceptions import InvalidMap
from dataclasses_avroschema.faker import fake

from . import field_utils
from .base import Field

PY_VER = sys.version_info

if PY_VER >= (3, 9):  # pragma: no cover
    GenericAlias = (typing.GenericAlias, typing._GenericAlias, typing._SpecialGenericAlias, typing._UnionGenericAlias)  # type: ignore # noqa: E501
else:
    GenericAlias = typing._GenericAlias  # type: ignore  # pragma: no cover


__ALL__ = [
    "ImmutableField",
    "StringField",
    "IntField",
    "LongField",
    "BooleanField",
    "DoubleField",
    "FloatField",
    "BytesField",
    "NoneField",
    "ContainerField",
    "ListField",
    "TupleField",
    "DictField",
    "UnionField",
    "FixedField",
    "EnumField",
    "SelfReferenceField",
    "DateField",
    "DatetimeField",
    "DatetimeMicroField",
    "TimeMilliField",
    "TimeMicroField",
    "UUIDField",
    "DecimalField",
    "RecordField",
    "AvroField",
]


class ImmutableField(Field):
    def get_avro_type(self) -> typing.Union[str, typing.List, typing.Dict[str, typing.Any]]:
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

    def default_to_avro(self, item: bytes) -> str:
        return item.decode()

    def fake(self) -> bytes:
        return fake.pystr().encode()


@dataclasses.dataclass
class NoneField(ImmutableField):
    @property
    def avro_type(self) -> str:
        return field_utils.NULL


@dataclasses.dataclass
class ContainerField(Field):
    @property
    def avro_type(self) -> typing.Dict:
        ...  # pragma: no cover

    def get_avro_type(self) -> types.JsonDict:
        avro_type = self.avro_type
        avro_type["name"] = self.get_singular_name(self.name)

        return avro_type


@dataclasses.dataclass
class BaseListField(ContainerField):
    items_type: typing.Any = None
    internal_field: Field = dataclasses.field(init=False)

    @property
    def avro_type(self) -> typing.Dict:
        self.generate_items_type()
        return {"type": field_utils.ARRAY, "items": self.items_type}

    def get_default_value(self) -> typing.Union[typing.List, dataclasses._MISSING_TYPE]:
        default = super().get_default_value()

        if default is not dataclasses.MISSING:
            if default is None:
                return []
            else:
                if isinstance(default, tuple):
                    default = list(default)
        return default

    def validate_default(self, default):
        assert isinstance(default, list), f"List is required as default for field {self.name}"
        if not isinstance(self.internal_field, UnionField):
            for element in default:
                self.internal_field.validate_default(element)

    def default_to_avro(self, values: typing.List):
        return [self.internal_field.default_to_avro(item) for item in values]

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


@dataclasses.dataclass
class ListField(BaseListField):
    def fake(self) -> typing.List:
        return [self.internal_field.fake()]


@dataclasses.dataclass
class TupleField(BaseListField):
    """
    This behaves on the same way as `ListField` with
    as in avro schema does not exist `tuples`

    The reason to have this is to generate a proper `fake`
    """

    def fake(self) -> typing.Tuple:
        return (self.internal_field.fake(),)


@dataclasses.dataclass
class DictField(ContainerField):
    values_type: typing.Any = None
    internal_field: typing.Any = None

    def __post_init__(self) -> None:
        key_type = self.type.__args__[0]

        if key_type is not str:
            raise InvalidMap(self.name, key_type)

    @property
    def avro_type(self) -> types.JsonDict:
        self.generate_values_type()
        return {"type": field_utils.MAP, "values": self.values_type}

    def get_default_value(self) -> typing.Union[types.JsonDict, dataclasses._MISSING_TYPE]:
        default = super().get_default_value()

        if default is not dataclasses.MISSING:
            if default is None:
                return {}
            else:
                assert isinstance(default, dict), f"Dict is required as default for field {self.name}"
        return default

    def validate_default(self, default):
        assert isinstance(default, dict)
        if not isinstance(self.internal_field, UnionField):
            for element in default.values():
                self.internal_field.validate_default(element)

    def default_to_avro(self, default: typing.Dict):
        return {key: self.internal_field.default_to_avro(value) for key, value in default.items()}

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
class UnionField(Field):
    unions: typing.List = dataclasses.field(default_factory=list)
    internal_fields: typing.List[Field] = dataclasses.field(default_factory=list)
    elements: typing.Tuple = dataclasses.field(default_factory=tuple)

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
        self.elements = get_args(self.type)
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

        for element in self.elements:
            # create the field and get the avro type
            field = AvroField(name, element, model_metadata=self.model_metadata, parent=self.parent)
            avro_type = field.get_avro_type()

            if avro_type not in unions and avro_type not in [
                e.get("name", None) for e in unions if isinstance(e, dict)
            ]:
                unions.append(avro_type)
                self.internal_fields.append(field)

        return unions

    def get_avro_type(self) -> typing.List:
        self.unions = self.generate_unions_type()
        return self.unions

    def default_to_avro(self, default: typing.Any):
        first_type = self.internal_fields[0]
        return first_type.default_to_avro(default)

    def validate_default(self, default):
        first_type = self.internal_fields[0]
        first_type.validate_default(default)

    def fake(self) -> typing.Any:
        # get a random internal field and return a fake value
        field = random.choice(self.internal_fields)
        return field.fake()


@dataclasses.dataclass
class FixedField(BytesField):
    field_info: typing.Optional[types.FixedFieldInfo] = None
    size: int = 0
    aliases: typing.Optional[typing.List[str]] = None
    namespace: typing.Optional[str] = None

    def __post_init__(self) -> None:
        self.set_fixed()

    def set_fixed(self) -> None:
        if self.field_info is not None:
            self.size = self.field_info.size
            self.aliases = self.field_info.aliases
            self.namespace = self.field_info.namespace

    def get_avro_type(self) -> types.JsonDict:
        avro_type = {
            "type": field_utils.FIXED,
            "name": self.get_singular_name(self.name),
            "size": int(self.size),
        }

        if self.namespace is not None:
            avro_type["namespace"] = self.namespace

        if self.aliases is not None:
            avro_type["aliases"] = self.aliases

        return avro_type

    def validate_default(self, default) -> bool:
        msg = "Invalid default type. Default should be bytes"
        assert isinstance(default, bytes), msg
        return True

    def fake(self) -> bytes:
        return fake.pystr(max_chars=self.size).encode()


@dataclasses.dataclass
class EnumField(Field):
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

    def get_avro_type(self) -> typing.Union[str, types.JsonDict]:
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
                return name
            else:
                return f"{namespace}.{name}"

    def default_to_avro(self, default: typing.Any) -> typing.Any:
        return default.value

    def fake(self) -> typing.Any:
        return random.choice(self.get_symbols())


@dataclasses.dataclass
class SelfReferenceField(Field):
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


@dataclasses.dataclass
class DateField(ImmutableField):
    """
    The date logical type represents a date within the calendar,
    with no reference to a particular time zone or time of day.

    A date logical type annotates an Avro int, where the int stores
    the number of days from the unix epoch, 1 January 1970 (ISO calendar).
    """

    @property
    def avro_type(self) -> typing.Dict:
        return field_utils.LOGICAL_DATE

    def default_to_avro(self, date: datetime.date) -> int:
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
class TimeMilliField(ImmutableField):
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

    def default_to_avro(self, time: datetime.time) -> int:
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
class TimeMicroField(ImmutableField):
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

    def default_to_avro(self, time: datetime.time) -> float:
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
        datetime_object: datetime.datetime = fake.date_time(tzinfo=datetime.timezone.utc)
        datetime_object = datetime_object + datetime.timedelta(microseconds=random.randint(0, 999))
        return datetime_object.time()


@dataclasses.dataclass
class DatetimeField(ImmutableField):
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

    def default_to_avro(self, date_time: datetime.datetime) -> int:
        """
        Returns the number of milliseconds from the unix epoch,
        1 January 1970 00:00:00.000 UTC for a given datetime
        """
        if date_time.tzinfo:
            ts = (date_time - utils.epoch).total_seconds()
        else:
            ts = (date_time - utils.epoch_naive).total_seconds()

        return int(ts * 1000)

    def fake(self) -> datetime.datetime:
        return fake.date_time(tzinfo=datetime.timezone.utc)


@dataclasses.dataclass
class DatetimeMicroField(ImmutableField):
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

    def default_to_avro(self, date_time: datetime.datetime) -> int:
        """
        Returns the number of milliseconds from the unix epoch,
        1 January 1970 00:00:00.000000 UTC for a given datetime
        """
        if date_time.tzinfo:
            ts = (date_time - utils.epoch).total_seconds()
        else:
            ts = (date_time - utils.epoch_naive).total_seconds()

        return int(ts * 1000000)

    def fake(self) -> datetime.datetime:
        datetime_object: datetime.datetime = fake.date_time(tzinfo=datetime.timezone.utc)
        return datetime_object + datetime.timedelta(microseconds=random.randint(0, 999))


@dataclasses.dataclass
class UUIDField(ImmutableField):
    @property
    def avro_type(self) -> typing.Dict:
        return field_utils.LOGICAL_UUID

    def validate_default(self, default) -> bool:
        msg = f"Invalid default type. Default should be {str} or {uuid.UUID}"
        assert isinstance(default, (str, uuid.UUID)), msg

        return True

    def default_to_avro(self, uuid: uuid.UUID) -> str:
        return str(uuid)

    def fake(self) -> uuid.UUID:
        return uuid.uuid4()


@dataclasses.dataclass
class DecimalField(Field):
    field_info: typing.Optional[types.DecimalFieldInfo] = None
    max_digits: int = -1  # amount of digits, in avro is called `precision`
    decimal_places: int = 0  # amount of digits to the right side, in avro is called `scale`

    def __post_init__(self) -> None:
        self.set_precision_scale()

    def set_precision_scale(self) -> None:
        if self.field_info is not None:
            self.max_digits = self.field_info.max_digits
            self.decimal_places = self.field_info.decimal_places

        # Validation on precision and scale per Avro schema
        if self.max_digits <= 0:
            raise ValueError("`max_digits` must be a positive integer greater than zero")

        if self.decimal_places < 0 or self.max_digits < self.decimal_places:
            raise ValueError("`decimal_places` must be zero or a positive integer less than or equal to the precision.")

    def get_avro_type(self) -> typing.Union[types.JsonDict, typing.List[typing.Union[str, types.JsonDict]]]:
        avro_type = {
            "type": field_utils.BYTES,
            "logicalType": field_utils.DECIMAL,
            "precision": self.max_digits,
            "scale": self.decimal_places,
        }

        if self.default is None:
            return ["null", avro_type]

        return avro_type

    def default_to_avro(self, default: decimal.Decimal) -> str:
        return serialization.decimal_to_str(default, self.max_digits, self.decimal_places)

    def fake(self) -> decimal.Decimal:
        return fake.pydecimal(right_digits=self.decimal_places, left_digits=self.max_digits - self.decimal_places)


@dataclasses.dataclass
class RecordField(Field):
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
                record_type = name
            else:
                record_type = f"{metadata.namespace}.{name}"

        if self.default is None:
            return [field_utils.NULL, record_type]
        return record_type

    def default_to_avro(self, value: "schema_generator.AvroModel") -> typing.Dict:
        return value.to_dict()

    def fake(self) -> typing.Any:
        return self.type.fake()


from .mapper import (
    CONTAINER_FIELDS_CLASSES,
    INMUTABLE_FIELDS_CLASSES,
    LOGICAL_TYPES_FIELDS_CLASSES,
    SPECIAL_ANNOTATED_TYPES,
)

LOGICAL_CLASSES = LOGICAL_TYPES_FIELDS_CLASSES.keys()


def field_factory(
    name: str,
    native_type: typing.Any,
    parent: typing.Any = None,
    *,
    default: typing.Any = dataclasses.MISSING,
    default_factory: typing.Any = dataclasses.MISSING,
    metadata: typing.Optional[typing.Dict[str, typing.Any]] = None,
    model_metadata: typing.Optional[utils.SchemaMetadata] = None,
) -> Field:
    from dataclasses_avroschema import AvroModel

    if metadata is None:
        metadata = {}

    field_info = None

    if native_type not in types.CUSTOM_TYPES and utils.is_annotated(native_type):
        a_type, *extra_args = get_args(native_type)
        field_info = next((arg for arg in extra_args if isinstance(arg, types.FieldInfo)), None)

        if field_info is None or a_type in (decimal.Decimal, types.Fixed):
            # it means that it is a custom type defined by us
            # `Int32`, `Float32`,`TimeMicro` or `DateTimeMicro`
            # or a type Annotated with the end user
            native_type = a_type

    if native_type in INMUTABLE_FIELDS_CLASSES:
        klass = INMUTABLE_FIELDS_CLASSES[native_type]
        return klass(
            name=name,
            type=native_type,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )

    # special case for some dynamic pydantic types (especially constraint types)
    # when a type cannot be imported and needs to be referenced by qualified string
    # see pydantic conint() implementation for more information
    elif inspect.isclass(native_type) and f"{native_type.__name__}" in INMUTABLE_FIELDS_CLASSES:
        klass = INMUTABLE_FIELDS_CLASSES[f"{native_type.__name__}"]
        return klass(
            name=name,
            type=native_type,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )

    elif utils.is_self_referenced(native_type):
        return SelfReferenceField(
            name=name,
            type=native_type,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif native_type in (types.Fixed, decimal.Decimal):
        klass = SPECIAL_ANNOTATED_TYPES[native_type]  # type: ignore
        return klass(  # type: ignore
            name=name,
            type=native_type,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
            field_info=field_info,
        )
    elif native_type in LOGICAL_TYPES_FIELDS_CLASSES:
        klass = LOGICAL_TYPES_FIELDS_CLASSES[native_type]  # type: ignore

        return klass(
            name=name,
            type=native_type,
            default=default,
            default_factory=default_factory,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif isinstance(native_type, GenericAlias):  # type: ignore
        origin = get_origin(native_type)

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
            default_factory=default_factory,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif inspect.isclass(native_type) and issubclass(native_type, enum.Enum):
        return EnumField(
            name=name,
            type=native_type,
            default=default,
            default_factory=default_factory,
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
            default_factory=default_factory,
            metadata=metadata,
            model_metadata=model_metadata,
            parent=parent,
        )
    elif inspect.isclass(native_type) and issubclass(native_type, AvroModel):
        return RecordField(
            name=name,
            type=native_type,
            default=default,
            default_factory=default_factory,
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
