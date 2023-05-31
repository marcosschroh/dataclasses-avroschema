import collections
import datetime
import decimal
import typing
import uuid

from dataclasses_avroschema import fields, types

BASE_INMUTABLE_FIELDS_CLASSES = {
    bool: fields.BooleanField,
    int: fields.LongField,
    types.Int32: fields.IntField,
    float: fields.DoubleField,
    types.Float32: fields.FloatField,
    bytes: fields.BytesField,
    str: fields.StringField,
    type(None): fields.NoneField,
}

BASE_CONTAINER_FIELDS_CLASSES = {
    tuple: fields.TupleField,
    list: fields.ListField,
    collections.abc.Sequence: fields.ListField,
    collections.abc.MutableSequence: fields.ListField,
    dict: fields.DictField,
    collections.abc.Mapping: fields.DictField,
    collections.abc.MutableMapping: fields.DictField,
    typing.Union: fields.UnionField,
}

BASE_LOGICAL_TYPES_FIELDS_CLASSES = {
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
