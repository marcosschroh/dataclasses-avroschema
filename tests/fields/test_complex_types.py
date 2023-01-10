import dataclasses
import datetime
import enum
import typing

import pytest
from faker import Faker

from dataclasses_avroschema import AvroModel, exceptions, field_utils, fields, types

from . import consts

faker = Faker()


class Color(enum.Enum):
    BLUE = "Blue"
    GREEN = "Green"
    YELLOW = "Yellow"

    class Meta:
        aliases = ["one", "two"]
        doc = "colors"
        namespace = "some.name.space"


def test_invalid_type_container_field():
    python_type = typing.Set
    name = "test_field"
    msg = f"Invalid Type for field {name}. Accepted types are list, tuple, dict or typing.Union"

    with pytest.raises(ValueError, match=msg):
        fields.AvroField(name, python_type, default=dataclasses.MISSING)


@pytest.mark.parametrize("sequence, python_primitive_type,python_type_str", consts.SEQUENCES_AND_TYPES)
def test_sequence_type(sequence, python_primitive_type, python_type_str):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[python_primitive_type]
    field = fields.AvroField(name, python_type, default=dataclasses.MISSING)

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, default=None)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [],
    }

    assert expected == field.to_dict()

    if python_type_str == field_utils.BYTES:
        values = [b"hola", b"hi"]
        default = ["hola", "hi"]
    else:
        values = default = faker.pylist(2, True, python_primitive_type)

    field = fields.AvroField(name, python_type, default=default, default_factory=lambda: values)

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": default,
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize(
    "sequence,python_primitive_type,python_type_str,value",
    consts.SEQUENCES_LOGICAL_TYPES,
)
def test_sequence_with_logical_type(sequence, python_primitive_type, python_type_str, value):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[python_primitive_type]

    field = fields.AvroField(name, python_type, default=dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, default=None)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [],
    }

    assert expected == field.to_dict()

    values = [value]

    field = fields.AvroField(name, python_type, default=values, default_factory=lambda: values)

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [fields.LOGICAL_TYPES_FIELDS_CLASSES[python_primitive_type].to_avro(value) for value in values],
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("union,items,default", consts.ARRAY_WITH_UNION_TYPES)
def test_sequence_with_union_type(union, items, default):
    name = "an_array_field"
    python_type = typing.List[union]

    field = fields.AvroField(name, python_type, default=dataclasses.MISSING)
    expected = {"name": name, "type": {"type": "array", "name": name, "items": items}}

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, default_factory=lambda: default)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": items},
        "default": default,
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, default=None)
    items.insert(0, field_utils.NULL)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": items},
        "default": [],
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("mapping,python_primitive_type,python_type_str", consts.MAPPING_AND_TYPES)
def test_mapping_type(mapping, python_primitive_type, python_type_str):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = mapping[str, python_primitive_type]

    field = fields.AvroField(name, python_type, default=dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, default=None)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": {},
    }

    assert expected == field.to_dict()

    if python_type_str == field_utils.BYTES:
        value = {"hola": b"hi"}
        default = {"hola": "hi"}
    else:
        value = default = faker.pydict(2, True, python_primitive_type)

    field = fields.AvroField(name, python_type, default=default, default_factory=lambda: value)

    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": default,
    }

    assert expected == field.to_dict()


def test_invalid_map():
    name = "a_map_field"
    python_type = typing.Dict[int, str]

    with pytest.raises(exceptions.InvalidMap) as excinfo:
        fields.AvroField(name, python_type, default=dataclasses.MISSING)

    msg = "Invalid map on field a_map_field. Keys must be string not <class 'int'>"
    assert msg == str(excinfo.value)


@pytest.mark.parametrize("mapping,python_primitive_type,python_type_str,value", consts.MAPPING_LOGICAL_TYPES)
def test_mapping_logical_type(mapping, python_primitive_type, python_type_str, value):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = mapping[str, python_primitive_type]

    field = fields.AvroField(name, python_type, default=dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, default=None)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": {},
    }

    assert expected == field.to_dict()

    values = {"key": value}
    field = fields.AvroField(name, python_type, default=dataclasses.MISSING, default_factory=lambda: values)

    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": {
            key: fields.LOGICAL_TYPES_FIELDS_CLASSES[python_primitive_type].to_avro(value)
            for key, value in values.items()
        },
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("union, avro_types", consts.UNION_PRIMITIVE_ELEMENTS)
def test_union_type(union, avro_types) -> None:
    name = "an_union_field"
    field = fields.AvroField(name, union)
    expected = {"name": name, "type": [*avro_types]}

    assert expected == field.to_dict()


# Tests to make sure defaults work, and that defaults are sorted to the beginning of the union
@pytest.mark.parametrize("union, avro_types, default", consts.UNION_PRIMITIVE_ELEMENTS_DEFAULTS)
def test_union_type_with_default(union, avro_types, default) -> None:
    name = "an_union_field"
    field = fields.AvroField(name, union, default=default)

    if isinstance(default, datetime.datetime):
        default = int((default - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
    elif isinstance(default, bytes):
        default = default.decode()

    expected = {"name": name, "type": [*avro_types], "default": default}

    assert expected == field.to_dict()


@pytest.mark.parametrize("union, avro_types", consts.UNION_WITH_ARRAY)
def test_union_with_arrays(union, avro_types) -> None:
    name = "an_union_field"
    field = fields.AvroField(name, union)

    expected = {"name": name, "type": [{"type": "array", "name": name, "items": avro_types[0]}, avro_types[1]]}

    assert expected == field.to_dict()


@pytest.mark.parametrize("union, avro_types", consts.UNION_WITH_MAP)
def test_union_with_maps(union, avro_types) -> None:
    name = "an_union_field"
    field = fields.AvroField(name, union)

    expected = {"name": name, "type": [{"type": "map", "name": name, "values": avro_types[0]}, avro_types[1]]}

    assert expected == field.to_dict()


@pytest.mark.parametrize("complex_type, avro_type", consts.OPTIONAL_UNION_COMPLEX_TYPES)
def test_union_as_optional_with_complex_types(complex_type, avro_type) -> None:
    """
    Test cases when typing.Optional is used.
    The result of typing.Optional[Any] is typing.Union[Any, NoneType]

    Always NoneType is placed at the end
    """
    name = "optional_field"
    python_type = typing.Optional[complex_type]
    field = fields.AvroField(name, python_type)

    expected = {"name": name, "type": [avro_type, "null"]}

    assert expected == field.to_dict()


@pytest.mark.parametrize("primitive_type, avro_type", consts.PRIMITIVE_TYPES)
def test_union_as_optional_with_primitives(primitive_type, avro_type) -> None:
    """
    Test cases when typing.Optional is used.
    The result of typing.Optional[Any] is typing.Union[Any, NoneType]

    Always NoneType is placed at the end
    """
    name = "an_optional_union_field"
    python_type = typing.Optional[primitive_type]
    field = fields.AvroField(name, python_type)

    expected = {"name": name, "type": [avro_type, "null"]}

    assert expected == field.to_dict()


def test_union_type_with_records():
    class User(AvroModel):
        "User"
        first_name: str

    class Car(AvroModel):
        "Car"
        engine_name: str

    class UnionRecord(AvroModel):
        an_union_field: typing.Union[User, Car]

    schema = UnionRecord.avro_schema_to_python()

    expected = {
        "name": "an_union_field",
        "type": [
            {
                "name": "User",
                "type": "record",
                "doc": "User",
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
    }

    assert expected == schema["fields"][0]


def test_union_type_with_record_default():
    class User(AvroModel):
        "User"
        first_name: str

    class Car(AvroModel):
        "Car"
        engine_name: str

    class UnionRecord(AvroModel):
        an_union_field: typing.Optional[typing.Union[User, Car]] = None

    schema = UnionRecord.avro_schema_to_python()

    expected = {
        "name": "an_union_field",
        "type": [
            field_utils.NULL,
            {
                "name": "User",
                "type": "record",
                "doc": "User",
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
        "default": None,
    }

    assert expected == schema["fields"][0]

    class UnionRecordTwo(AvroModel):
        an_union_field: typing.Union[User, Car] = dataclasses.field(default_factory=lambda: {"first_name": "a name"})

    schema = UnionRecordTwo.avro_schema_to_python()
    expected = {
        "name": "an_union_field",
        "type": [
            {
                "name": "User",
                "type": "record",
                "doc": "User",
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "Car",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
        "default": {"first_name": "a name"},
    }

    assert expected == schema["fields"][0]


def test_fixed_type():
    """
    When the type is types.Fixed, the Avro field type should be fixed
    with size attribute present.
    """
    name = "a_fixed_field"
    namespace = "md5"
    aliases = ["md5", "hash"]
    default = types.Fixed(16, namespace=namespace, aliases=aliases)
    python_type = types.Fixed
    field = fields.AvroField(name, python_type, default=default)

    expected = {
        "name": name,
        "type": {
            "type": "fixed",
            "name": name,
            "size": default.size,
            "namespace": namespace,
            "aliases": aliases,
        },
    }

    assert expected == field.to_dict()


def test_enum_type():
    """
    When the type is enum.Enum, the Avro field type should be Enum
    with symbols attribute present.
    """
    name = "an_enum_field"
    namespace = "my_enum"
    aliases = ["enum", "first enum"]
    parent = AvroModel()

    class CardType(enum.Enum):
        SPADES = "SPADES"
        HEARTS = "HEARTS"
        DIAMONDS = "DIAMONDS"
        CLUBS = "CLUBS"

        class Meta:
            namespace = "my_enum"
            aliases = ["enum", "first enum"]

    python_type = CardType
    field = fields.AvroField(name, python_type, default=CardType.CLUBS, parent=parent)
    symbols = ["SPADES", "HEARTS", "DIAMONDS", "CLUBS"]

    expected = {
        "name": name,
        "type": {
            "type": "enum",
            "name": "CardType",
            "symbols": symbols,
            "namespace": namespace,
            "aliases": aliases,
        },
        "default": CardType.CLUBS.value,
    }

    assert expected == field.to_dict()

    class CardType(enum.Enum):
        SPADES = "SPADES"
        HEARTS = "HEARTS"
        DIAMONDS = "DIAMONDS"
        CLUBS = "CLUBS"

        class Meta:
            namespace = "my_enum"

    python_type = CardType
    field = fields.AvroField(name, python_type, parent=parent)

    expected = {"name": name, "type": {"type": "enum", "name": "CardType", "symbols": symbols, "namespace": namespace}}

    assert expected == field.to_dict()

    class CardType(enum.Enum):
        SPADES = "SPADES"
        HEARTS = "HEARTS"
        DIAMONDS = "DIAMONDS"
        CLUBS = "CLUBS"

    python_type = CardType
    field = fields.AvroField(name, python_type, default=None, parent=parent)

    expected = {
        "name": name,
        "type": {
            "type": "enum",
            "name": "CardType",
            "symbols": symbols,
        },
        "default": None,
    }

    assert expected == field.to_dict()

    python_type = typing.Optional[CardType]
    parent.user_defined_types = set()
    field = fields.AvroField(name, python_type, default=None, parent=parent)

    expected = {
        "name": name,
        "type": [
            "null",
            {
                "type": "enum",
                "name": "CardType",
                "symbols": symbols,
            },
        ],
        "default": None,
    }

    assert expected == field.to_dict()

    with pytest.raises(AssertionError):

        class CardType(enum.Enum):
            SPADES = "SPADES"
            HEARTS = "HEARTS"
            DIAMONDS = "DIAMONDS"
            CLUBS = "CLUBS"

        class RandomType(enum.Enum):
            SOMETHING = "SOMETHING"

        python_type = CardType
        field = fields.AvroField(name, python_type, default=RandomType.SOMETHING, parent=parent)
        field.to_dict()


def test_enum_field():
    enum_field = fields.AvroField(
        "field_name", Color, default=Color.BLUE, metadata={"key": "value"}, parent=AvroModel()
    )

    assert enum_field.get_symbols() == ["Blue", "Green", "Yellow"]
    assert enum_field._get_meta_class_attributes() == {
        "aliases": ["one", "two"],
        "doc": "colors",
        "namespace": "some.name.space",
    }
    assert enum_field.get_avro_type() == {
        "type": "enum",
        "name": "Color",
        "symbols": ["Blue", "Green", "Yellow"],
        "aliases": ["one", "two"],
        "doc": "colors",
        "namespace": "some.name.space",
    }

    assert enum_field.get_default_value() == "Blue"


def test_enum_field_default():
    enum_field1 = fields.AvroField("field_name", Color, default=types.MissingSentinel, metadata={"key": "value"})
    enum_field2 = fields.AvroField("field_name", Color, default=dataclasses.MISSING, metadata={"key": "value"})
    enum_field3 = fields.AvroField("field_name", Color, default=None, metadata={"key": "value"})
    enum_field4 = fields.AvroField("field_name", Color, default=Color.GREEN, metadata={"key": "value"})

    assert enum_field1.get_default_value() == dataclasses.MISSING
    assert enum_field2.get_default_value() == dataclasses.MISSING
    assert enum_field3.get_default_value() is None
    assert enum_field4.get_default_value() == "Green"
