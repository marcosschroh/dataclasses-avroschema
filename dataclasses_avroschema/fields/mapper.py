import collections
import datetime
import decimal
import typing
import uuid

from dataclasses_avroschema import types

from . import fields, pydantic_fields

INMUTABLE_FIELDS_CLASSES = {
    bool: fields.BooleanField,
    int: fields.LongField,
    types.Int32: fields.IntField,
    float: fields.DoubleField,
    types.Float32: fields.FloatField,
    bytes: fields.BytesField,
    str: fields.StringField,
    type(None): fields.NoneField,
}

CONTAINER_FIELDS_CLASSES = {
    tuple: fields.TupleField,
    list: fields.ListField,
    collections.abc.Sequence: fields.ListField,
    collections.abc.MutableSequence: fields.ListField,
    dict: fields.DictField,
    collections.abc.Mapping: fields.DictField,
    collections.abc.MutableMapping: fields.DictField,
    typing.Union: fields.UnionField,
}

LOGICAL_TYPES_FIELDS_CLASSES = {
    datetime.date: fields.DateField,
    datetime.time: fields.TimeMilliField,
    types.TimeMicro: fields.TimeMicroField,
    datetime.datetime: fields.DatetimeField,
    types.DateTimeMicro: fields.DatetimeMicroField,
    uuid.uuid4: fields.UUIDField,
    uuid.UUID: fields.UUIDField,
    bytes: fields.BytesField,
}

SPECIAL_ANNOTATED_TYPES = {
    decimal.Decimal: fields.DecimalField,
    types.Fixed: fields.FixedField,
}

PYDANTIC_TYPES = None

try:
    import pydantic  # pragma: no cover

    PYDANTIC_INMUTABLE_FIELDS_CLASSES = {
        pydantic.FilePath: pydantic_fields.FilePathField,
        pydantic.DirectoryPath: pydantic_fields.DirectoryPathField,
        pydantic.EmailStr: pydantic_fields.EmailStrField,
        pydantic.NameEmail: pydantic_fields.NameEmailField,
        pydantic.AnyUrl: pydantic_fields.AnyUrlField,
        pydantic.AnyHttpUrl: pydantic_fields.AnyHttpUrlField,
        pydantic.HttpUrl: pydantic_fields.HttpUrlField,
        pydantic.FileUrl: pydantic_fields.FileUrlField,
        pydantic.PostgresDsn: pydantic_fields.PostgresDsnField,
        pydantic.CockroachDsn: pydantic_fields.CockroachDsnField,
        pydantic.AmqpDsn: pydantic_fields.AmqpDsnField,
        pydantic.RedisDsn: pydantic_fields.RedisDsnField,
        pydantic.MongoDsn: pydantic_fields.MongoDsnField,
        pydantic.KafkaDsn: pydantic_fields.KafkaDsnField,
        pydantic.SecretStr: pydantic_fields.SecretStrField,
        pydantic.IPvAnyAddress: pydantic_fields.IPvAnyAddressField,
        pydantic.IPvAnyInterface: pydantic_fields.IPvAnyInterfaceField,
        pydantic.IPvAnyNetwork: pydantic_fields.IPvAnyNetworkField,
        pydantic.NegativeFloat: pydantic_fields.NegativeFloatField,
        pydantic.PositiveFloat: pydantic_fields.PositiveFloatField,
        pydantic.NegativeInt: pydantic_fields.NegativeIntField,
        pydantic.PositiveInt: pydantic_fields.PositiveIntField,
        pydantic.ConstrainedInt: pydantic_fields.ConstrainedIntField,
        # ConstrainedIntValue is a dynamic type that needs to be referenced by qualified name
        # and cannot be imported directly
        "pydantic.types.ConstrainedIntValue": pydantic_fields.ConstrainedIntField,
    }

    PYDANTIC_LOGICAL_TYPES_FIELDS_CLASSES = {
        pydantic.UUID1: pydantic_fields.UUID1Field,
        pydantic.UUID3: pydantic_fields.UUID3Field,
        pydantic.UUID4: pydantic_fields.UUID4Field,
        pydantic.UUID5: pydantic_fields.UUID5Field,
    }

    INMUTABLE_FIELDS_CLASSES.update(PYDANTIC_INMUTABLE_FIELDS_CLASSES)
    LOGICAL_TYPES_FIELDS_CLASSES.update(PYDANTIC_LOGICAL_TYPES_FIELDS_CLASSES)  # type: ignore
    PYDANTIC_TYPES = (
        pydantic.FilePath,
        pydantic.DirectoryPath,
        pydantic.EmailStr,
        pydantic.NameEmail,
        pydantic.AnyUrl,
        pydantic.AnyHttpUrl,
        pydantic.HttpUrl,
        pydantic.FileUrl,
        pydantic.PostgresDsn,
        pydantic.CockroachDsn,
        pydantic.AmqpDsn,
        pydantic.RedisDsn,
        pydantic.MongoDsn,
        pydantic.KafkaDsn,
        pydantic.SecretStr,
        pydantic.IPvAnyAddress,
        pydantic.IPvAnyInterface,
        pydantic.IPvAnyNetwork,
        pydantic.NegativeFloat,
        pydantic.PositiveFloat,
        pydantic.NegativeInt,
        pydantic.PositiveInt,
        pydantic.ConstrainedInt,
        pydantic.UUID1,
        pydantic.UUID3,
        pydantic.UUID4,
        pydantic.UUID5,
    )

except ImportError:  # type: ignore # pragma: no cover
    # pydantic is not installed so we do not include their fields
    ...  # type: ignore # pragma: no cover
