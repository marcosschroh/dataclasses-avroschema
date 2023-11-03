import dataclasses
import datetime
import enum
import re
import typing

import pytest

from dataclasses_avroschema import AvroField, AvroModel, exceptions, types
from dataclasses_avroschema.fields import field_utils

from . import consts


class Color(enum.Enum):
    BLUE = "Blue"
    GREEN = "Green"
    YELLOW = "Yellow"

    class Meta:
        aliases = ["one", "two"]
        doc = "colors"
        namespace = "some.name.space"


class Suit(enum.Enum):
    SPADES = "SPADES"
    HEARTS = "HEARTS"
    DIAMONDS = "DIAMONDS"
    CLUBS = "CLUBS"


def test_invalid_type_container_field():
    python_type = typing.Set
    name = "test_field"
    msg = f"Invalid Type {python_type} for field {name}. Accepted types are list, tuple, dict, typing.Union, or typing.Literal"

    with pytest.raises(ValueError, match=msg):
        AvroField(name, python_type, default=dataclasses.MISSING)


@pytest.mark.parametrize("sequence, python_primitive_type,python_type_str", consts.SEQUENCES_AND_TYPES)
def test_sequence_type_with_no_default(sequence, python_primitive_type, python_type_str):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[python_primitive_type]
    field = AvroField(name, python_type, default=dataclasses.MISSING)

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("sequence, python_primitive_type,python_type_str", consts.SEQUENCES_AND_TYPES)
def test_sequence_type_with_null_default(sequence, python_primitive_type, python_type_str):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[python_primitive_type]
    field = AvroField(name, python_type, default=None)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [],
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("sequence, primitive_type,python_type_str", consts.SEQUENCES_AND_TYPES)
def test_sequence_type_with_default(sequence, primitive_type, python_type_str):
    name = "an_array_field"
    python_type = sequence[primitive_type]
    field = AvroField(name, python_type, default=dataclasses.MISSING)
    field.avro_type

    if python_type_str == field_utils.BYTES:
        values = [b"hola", b"hi"]
        default = ["hola", "hi"]
    else:
        values = default = field.fake()

    field = AvroField(name, python_type, default=values)

    # field = AvroField(name, python_type, default=values, default_factory=lambda: values)

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": list(default),
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize(
    "sequence,primitive_type,python_type_str,value",
    consts.SEQUENCES_LOGICAL_TYPES,
)
def test_sequence_with_logical_type_missing_default(sequence, primitive_type, python_type_str, value):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[primitive_type]

    field = AvroField(name, python_type, default=dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize(
    "sequence,primitive_type,python_type_str,value",
    consts.SEQUENCES_LOGICAL_TYPES,
)
def test_sequence_with_logical_type_none_default(sequence, primitive_type, python_type_str, value):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[primitive_type]

    field = AvroField(name, python_type, default=None)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [],
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize(
    "sequence,primitive_type,python_type_str,value",
    consts.SEQUENCES_LOGICAL_TYPES,
)
def test_sequence_with_logical_type_with_default(sequence, primitive_type, python_type_str, value):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[primitive_type]
    values = [value]
    field = AvroField(name, python_type, default=values, default_factory=lambda: values)
    field.avro_type

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": field.default_to_avro(values),
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("union,items,default", consts.ARRAY_WITH_UNION_TYPES)
def test_sequence_with_union_type_missing_default(union, items, default):
    name = "an_array_field"
    python_type = typing.List[union]

    field = AvroField(name, python_type, default=dataclasses.MISSING)
    expected = {"name": name, "type": {"type": "array", "name": name, "items": items}}

    assert expected == field.to_dict()


@pytest.mark.parametrize("union,items,default", consts.ARRAY_WITH_UNION_TYPES)
def test_sequence_with_union_type_with_default(union, items, default):
    name = "an_array_field"
    python_type = typing.List[union]
    field = AvroField(name, python_type, default_factory=lambda: default)

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": items},
        "default": default,
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("union,items,default", consts.ARRAY_WITH_UNION_TYPES)
def test_sequence_with_union_type_none_default(union, items, default):
    name = "an_array_field"
    python_type = typing.List[union]

    field = AvroField(name, python_type, default=None)
    items.insert(0, field_utils.NULL)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": items},
        "default": [],
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("mapping,primitive_type,python_type_str", consts.MAPPING_AND_TYPES)
def test_mapping_type_missing_default(mapping, primitive_type, python_type_str):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = mapping[str, primitive_type]

    field = AvroField(name, python_type, default=dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("mapping,primitive_type,python_type_str", consts.MAPPING_AND_TYPES)
def test_mapping_type_none_default(mapping, primitive_type, python_type_str):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = mapping[str, primitive_type]
    field = AvroField(name, python_type, default=None)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": {},
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("mapping,primitive_type,python_type_str", consts.MAPPING_AND_TYPES)
def test_mapping_type_with_default(mapping, primitive_type, python_type_str):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = mapping[str, primitive_type]
    field = AvroField(name, python_type, default=dataclasses.MISSING)
    field.avro_type

    if python_type_str == field_utils.BYTES:
        value = {"hola": b"hi"}
        default = {"hola": "hi"}
    else:
        value = default = field.fake()

    field = AvroField(name, python_type, default=default, default_factory=lambda: value)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": default,
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("mapping,primitive_type,python_type_str", consts.MAPPING_AND_TYPES)
def test_mapping_type_with_strenum_key(mapping, primitive_type, python_type_str):
    """
    When the type is Dict, the Avro field should accept keys whose type
    is derived from str since they are strings.
    """

    class DerivedStr(str):
        pass

    name = "a_map_field"
    python_type = mapping[DerivedStr, str]
    field = AvroField(name, python_type)

    expected = {
        "type": field_utils.MAP,
        "values": field_utils.STRING,
    }

    assert expected == field.avro_type

    # StrEnums should also be accepted
    class TheStrEnum(str, enum.Enum):
        pass

    python_type = mapping[TheStrEnum, str]
    field = AvroField(name, python_type)

    assert expected == field.avro_type


def test_invalid_map():
    name = "a_map_field"
    python_type = typing.Dict[int, str]

    with pytest.raises(exceptions.InvalidMap) as excinfo:
        AvroField(name, python_type, default=dataclasses.MISSING)

    msg = "Invalid map on field a_map_field. Keys must be string not <class 'int'>"
    assert msg == str(excinfo.value)


@pytest.mark.parametrize("mapping,primitive_type,python_type_str,value", consts.MAPPING_LOGICAL_TYPES)
def test_mapping_logical_type(mapping, primitive_type, python_type_str, value):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = mapping[str, primitive_type]

    field = AvroField(name, python_type, default=dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
    }

    assert expected == field.to_dict()

    field = AvroField(name, python_type, default=None)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": {},
    }

    assert expected == field.to_dict()

    values = {"key": value}
    field = AvroField(name, python_type, default=dataclasses.MISSING, default_factory=lambda: values)
    field.avro_type

    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": field.default_to_avro(values),
    }

    assert expected == field.to_dict()


@pytest.mark.parametrize("union, avro_types", consts.UNION_PRIMITIVE_ELEMENTS)
def test_union_type(union, avro_types) -> None:
    name = "an_union_field"
    field = AvroField(name, union)
    expected = {"name": name, "type": [*avro_types]}

    assert expected == field.to_dict()


# Tests to make sure defaults work, and that defaults are sorted to the beginning of the union
@pytest.mark.parametrize("union, avro_types, default", consts.UNION_PRIMITIVE_ELEMENTS_DEFAULTS)
def test_union_type_with_default(union, avro_types, default) -> None:
    name = "an_union_field"
    field = AvroField(name, union, default=default)

    if isinstance(default, datetime.datetime):
        default = int(default.timestamp() * 1000)
    elif isinstance(default, bytes):
        default = default.decode()

    expected = {"name": name, "type": [*avro_types], "default": default}

    assert expected == field.to_dict()


@pytest.mark.parametrize("union, avro_types", consts.UNION_WITH_ARRAY)
def test_union_with_arrays(union, avro_types) -> None:
    name = "an_union_field"
    field = AvroField(name, union)

    expected = {"name": name, "type": [{"type": "array", "name": name, "items": avro_types[0]}, avro_types[1]]}

    assert expected == field.to_dict()


@pytest.mark.parametrize("union, avro_types", consts.UNION_WITH_MAP)
def test_union_with_maps(union, avro_types) -> None:
    name = "an_union_field"
    field = AvroField(name, union)

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
    field = AvroField(name, python_type)

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
    field = AvroField(name, python_type)

    if python_type is type(None):
        expected = {"name": name, "type": "null"}
    else:
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


def test_union_type_with_record_none_default():
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


def test_union_type_with_record_default():
    class User(AvroModel):
        "User"
        first_name: str

    class Car(AvroModel):
        "Car"
        engine_name: str

    class UnionRecord(AvroModel):
        an_union_field: typing.Union[User, Car] = dataclasses.field(default_factory=lambda: User(first_name="a name"))

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
    python_type = types.confixed(size=16, aliases=aliases, namespace=namespace)
    field = AvroField(name, python_type)

    expected = {
        "name": name,
        "type": {
            "type": "fixed",
            "name": name,
            "size": 16,
            "namespace": namespace,
            "aliases": aliases,
        },
    }

    assert expected == field.to_dict()


def test_fixed_type_with_default():
    """
    When the type is types.Fixed, the Avro field type should be fixed
    with size attribute present.
    """
    name = "a_fixed_field"
    namespace = "md5"
    aliases = ["md5", "hash"]
    default = b"u00ffffffffffffx"
    python_type = types.confixed(size=16, aliases=aliases, namespace=namespace)
    field = AvroField(name, python_type, default=default)

    expected = {
        "name": name,
        "type": {
            "type": "fixed",
            "name": name,
            "size": 16,
            "namespace": namespace,
            "aliases": aliases,
        },
        "default": default.decode(),
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
    field = AvroField(name, python_type, default=CardType.CLUBS, parent=parent)
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
    field = AvroField(name, python_type, parent=parent)

    expected = {"name": name, "type": {"type": "enum", "name": "CardType", "symbols": symbols, "namespace": namespace}}

    assert expected == field.to_dict()

    class CardType(enum.Enum):
        SPADES = "SPADES"
        HEARTS = "HEARTS"
        DIAMONDS = "DIAMONDS"
        CLUBS = "CLUBS"

    python_type = CardType
    field = AvroField(name, python_type, default=None, parent=parent)

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
    parent._user_defined_types = set()
    field = AvroField(name, python_type, default=None, parent=parent)

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
        field = AvroField(name, python_type, default=RandomType.SOMETHING, parent=parent)
        field.to_dict()


def test_enum_field():
    enum_field = AvroField("field_name", Color, default=Color.BLUE, metadata={"key": "value"}, parent=AvroModel())

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

    assert enum_field.get_default_value() == Color.BLUE


def test_enum_field_default():
    enum_field1 = AvroField("field_name", Color, metadata={"key": "value"})
    enum_field2 = AvroField("field_name", Color, default=dataclasses.MISSING, metadata={"key": "value"})
    enum_field3 = AvroField("field_name", Color, default=None, metadata={"key": "value"})
    enum_field4 = AvroField("field_name", Color, default=Color.GREEN, metadata={"key": "value"})

    assert enum_field1.get_default_value() == dataclasses.MISSING
    assert enum_field2.get_default_value() == dataclasses.MISSING
    assert enum_field3.get_default_value() is None
    assert enum_field4.get_default_value() == Color.GREEN


@pytest.mark.parametrize("value", [4, "4", True, b"four", Color.BLUE, None])
def test_literal_field_with_single_parameter(value):
    """
    When the type is typing.Literal, the Avro field type should be the
    encapsulated value type (i.e. int, string, etc.)
    """
    name = "test_field"
    python_type = typing.Literal[value]  # type: ignore
    # Required for enums
    parent = AvroModel()
    parent._user_defined_types.clear()

    field = AvroField(name, python_type, parent)
    result = field.to_dict()

    # Verify the correct type conversion. Schema structure of resulting types
    # is validated by tests in this file that are specific to those types
    if isinstance(value, enum.Enum):
        assert result["type"]["type"] == field_utils.ENUM
    else:
        builtin_type = type(value)
        avro_type = field_utils.PYTHON_TYPE_TO_AVRO[builtin_type]
        assert result["type"] == avro_type

    # Reset the class variable
    parent._user_defined_types.clear()


def test_literal_field_with_multiple_parameters():
    """
    When the type is typing.Literal with multiple parameters, it should
    be converted to a Union of Literals
    """
    name = "test_field"
    python_type = typing.Literal[4, "4", True, b"four", Suit.SPADES]
    # Required for enums
    parent = AvroModel()
    parent._user_defined_types.clear()

    field = AvroField(name, python_type, parent)

    assert field.to_dict() == {
        "name": name,
        "type": [
            field_utils.LONG,
            field_utils.STRING,
            field_utils.BOOLEAN,
            field_utils.BYTES,
            {"type": field_utils.ENUM, "name": "Suit", "symbols": [s.value for s in Suit]},
        ],
    }

    # Reset the class variable
    parent._user_defined_types.clear()


@pytest.mark.parametrize(
    "default, avro_type, avro_default",
    [
        (4, field_utils.LONG, 4),
        ("4", field_utils.STRING, "4"),
        (True, field_utils.BOOLEAN, True),
        (b"four", field_utils.BYTES, "four"),
        (
            Suit.DIAMONDS,
            {"type": field_utils.ENUM, "name": "Suit", "symbols": [s.value for s in Suit]},
            Suit.DIAMONDS.value,
        ),
        (None, field_utils.NULL, None),
    ],
)
def test_literal_field_with_single_parameter_with_default(default, avro_type, avro_default):
    name = "test_field"
    python_type = typing.Literal[default]  # type: ignore
    parent = AvroModel()
    parent._user_defined_types.clear()

    field = AvroField(name, python_type, parent, default=default)

    assert field.to_dict() == {
        "name": name,
        "type": avro_type,
        "default": avro_default,
    }

    # Reset the class variable
    AvroModel._user_defined_types.clear()


def test_literal_field_with_multiple_parameters_with_default():
    """
    When the type is typing.Literal, type order behave like a UnionField
    when a default is present
    """
    name = "test_field"
    python_type = typing.Literal["one", b"two", True, 2, Suit.CLUBS, None]
    parent = AvroModel()
    parent._user_defined_types.clear()
    default = 2

    field = AvroField(name, python_type, parent, default=default)

    assert field.to_dict() == {
        "name": name,
        "type": [
            # Literal with multiple parameters is treated as a union, so the default's
            # type should be listed first
            field_utils.LONG,
            field_utils.STRING,
            field_utils.BYTES,
            field_utils.BOOLEAN,
            {"type": field_utils.ENUM, "name": "Suit", "symbols": [s.value for s in Suit]},
            field_utils.NULL,
        ],
        "default": default,
    }

    # Reset the class variable
    parent._user_defined_types.clear()


@pytest.mark.parametrize(
    "arg, default",
    [(4, "3"), ("4", 3), (b"four", "four"), (Color.YELLOW, Suit.SPADES)],
)
def test_literal_field_with_invalid_default(arg, default):
    """
    When the type is typing.Literal, AssertionError should be raised if
    the field is supplied a default of a type that does not match the
    type of the specified literal value
    """

    @dataclasses.dataclass
    class Model(AvroModel):
        test_field: typing.Literal[arg] = default  # type: ignore

    msg = f'Invalid default type {type(default)} for field "test_field". Default should be {type(arg)}'
    # We need to escape all of the special characters in msg to do a regex match
    matchable_msg = re.escape(msg)
    with pytest.raises(AssertionError, match=matchable_msg):
        Model.avro_schema()

    # Reset the class variable
    AvroModel._user_defined_types.clear()


def test_literal_field_with_no_parameters():
    """
    When the type is typing.Literal, TypeError should be raised if
    the field is annotated without any parameters
    """

    @dataclasses.dataclass
    class Model(AvroModel):
        test_field: typing.Literal

    msg = (
        f"Type {typing.Literal} for field test_field is unknown. Please check the valid types at "
        "https://marcosschroh.github.io/dataclasses-avroschema/fields_specification/#avro-field-and-python-types-summary"  # noqa: E501
    )
    matchable_msg = re.escape(msg)
    with pytest.raises(ValueError, match=matchable_msg):
        Model.avro_schema()

    # Reset the class variable
    AvroModel._user_defined_types.clear()
