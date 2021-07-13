import dataclasses
import datetime
import enum
import typing

import pytest
from faker import Faker

from dataclasses_avroschema import AvroModel, fields, types
from dataclasses_avroschema.fields import EnumField, UnionField

from . import consts

faker = Faker()


def test_invalid_type_container_field():
    python_type = typing.Set
    name = "test_field"
    msg = f"Invalid Type for field {name}. Accepted types are list, tuple, dict or typing.Union"

    with pytest.raises(ValueError, match=msg):
        fields.AvroField(name, python_type, dataclasses.MISSING)


@pytest.mark.parametrize("sequence, python_primitive_type,python_type_str", consts.SEQUENCES_AND_TYPES)
def test_sequence_type(sequence, python_primitive_type, python_type_str):
    """
    When the type is List, the Avro field type should be array
    with the items attribute present.
    """
    name = "an_array_field"
    python_type = sequence[python_primitive_type]
    field = fields.AvroField(name, python_type, dataclasses.MISSING)

    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, None)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
        "default": [],
    }

    assert expected == field.to_dict()

    if python_type_str == fields.BYTES:
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

    field = fields.AvroField(name, python_type, dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "array", "name": name, "items": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, None)
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
    items.insert(0, fields.NULL)
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

    field = fields.AvroField(name, python_type, dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, None)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
        "default": {},
    }

    assert expected == field.to_dict()

    if python_type_str == fields.BYTES:
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


@pytest.mark.parametrize("mapping,python_primitive_type,python_type_str,value", consts.MAPPING_LOGICAL_TYPES)
def test_mapping_logical_type(mapping, python_primitive_type, python_type_str, value):
    """
    When the type is Dict, the Avro field type should be map
    with the values attribute present. The keys are always string type.
    """
    name = "a_map_field"
    python_type = mapping[str, python_primitive_type]

    field = fields.AvroField(name, python_type, dataclasses.MISSING)
    expected = {
        "name": name,
        "type": {"type": "map", "name": name, "values": python_type_str},
    }

    assert expected == field.to_dict()

    field = fields.AvroField(name, python_type, None)
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


@pytest.mark.parametrize("primitive_types, avro_types, default", consts.UNION_PRIMITIVE_ELEMENTS)
def test_union_type(primitive_types, avro_types, default):
    name = "an_union_field"
    python_type = typing.Union[primitive_types]
    field = fields.AvroField(name, python_type)

    expected = {"name": name, "type": [*avro_types]}

    assert expected == field.to_dict()


# Tests to make sure defaults work, and that defaults are sorted to the beginning of the union
@pytest.mark.parametrize("primitive_types, avro_types, default", consts.UNION_PRIMITIVE_ELEMENTS_DEFAULTS)
def test_union_type_with_default(primitive_types, avro_types, default):
    name = "an_union_field"
    python_type = typing.Union[primitive_types]
    field = fields.AvroField(name, python_type, default=default)

    if isinstance(default, datetime.datetime):
        default = (default - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
    elif isinstance(default, bytes):
        default = default.decode()

    expected = {"name": name, "type": [*avro_types], "default": default}

    assert expected == field.to_dict()


@pytest.mark.parametrize("complex_type, avro_types", consts.UNION_WITH_ARRAY)
def test_union_with_arrays(complex_type, avro_types):
    name = "an_union_field"
    python_type = typing.Union[complex_type]
    field = fields.AvroField(name, python_type)

    expected = {"name": name, "type": [{"type": "array", "name": name, "items": avro_types[0]}, avro_types[1]]}

    assert expected == field.to_dict()


@pytest.mark.parametrize("complex_type, avro_types", consts.UNION_WITH_MAP)
def test_union_with_maps(complex_type, avro_types):
    name = "an_union_field"
    python_type = typing.Union[complex_type]
    field = fields.AvroField(name, python_type)

    expected = {"name": name, "type": [{"type": "map", "name": name, "values": avro_types[0]}, avro_types[1]]}

    assert expected == field.to_dict()


@pytest.mark.parametrize("complex_type, avro_type", consts.OPTIONAL_UNION_COMPLEX_TYPES)
def test_union_as_optional_with_complex_types(complex_type, avro_type):
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
def test_union_as_optional_with_primitives(primitive_type, avro_type):
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

    name = "an_union_field"
    python_type = typing.Union[User, Car]
    field = fields.AvroField(name, python_type)

    expected = {
        "name": name,
        "type": [
            {
                "name": "an_union_field_user_record",
                "type": "record",
                "doc": "User",
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "an_union_field_car_record",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
    }

    assert expected == field.to_dict()


def test_union_type_with_record_default():
    class User(AvroModel):
        "User"
        first_name: str

    class Car(AvroModel):
        "Car"
        engine_name: str

    name = "an_union_field"
    python_type = typing.Union[User, Car]
    field = fields.AvroField(name, python_type, None)

    expected = {
        "name": name,
        "type": [
            fields.NULL,
            {
                "name": "an_union_field_user_record",
                "type": "record",
                "doc": "User",
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "an_union_field_car_record",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
        "default": None,
    }

    assert expected == field.to_dict()

    field = fields.AvroField(
        name,
        python_type,
        default=dataclasses.MISSING,
        default_factory=lambda: {"first_name": "a name"},
    )

    expected = {
        "name": name,
        "type": [
            {
                "name": "an_union_field_user_record",
                "type": "record",
                "doc": "User",
                "fields": [{"name": "first_name", "type": "string"}],
            },
            {
                "name": "an_union_field_car_record",
                "type": "record",
                "doc": "Car",
                "fields": [{"name": "engine_name", "type": "string"}],
            },
        ],
        "default": {"first_name": "a name"},
    }

    assert expected == field.to_dict()


def test_union_field_enum_default():
    union_field = UnionField("some_field", typing.Union[None, Color], Color.BLUE)
    assert union_field.get_default_value() == "Blue"


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
    field = fields.AvroField(name, python_type, default)

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

    class CardType(enum.Enum):
        SPADES = "SPADES"
        HEARTS = "HEARTS"
        DIAMONDS = "DIAMONDS"
        CLUBS = "CLUBS"

        class Meta:
            namespace = "my_enum"
            aliases = ["enum", "first enum"]

    python_type = CardType
    field = fields.AvroField(name, python_type, default=CardType.CLUBS)
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
    field = fields.AvroField(name, python_type)

    expected = {"name": name, "type": {"type": "enum", "name": "CardType", "symbols": symbols, "namespace": namespace}}

    assert expected == field.to_dict()

    class CardType(enum.Enum):
        SPADES = "SPADES"
        HEARTS = "HEARTS"
        DIAMONDS = "DIAMONDS"
        CLUBS = "CLUBS"

    python_type = CardType
    field = fields.AvroField(name, python_type, default=None)

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

    with pytest.raises(AssertionError):

        class CardType(enum.Enum):
            SPADES = "SPADES"
            HEARTS = "HEARTS"
            DIAMONDS = "DIAMONDS"
            CLUBS = "CLUBS"

        class RandomType(enum.Enum):
            SOMETHING = "SOMETHING"

        python_type = CardType
        field = fields.AvroField(name, python_type, default=RandomType.SOMETHING)

        field.to_dict()


class Color(enum.Enum):
    BLUE = "Blue"
    GREEN = "Green"
    YELLOW = "Yellow"

    class Meta:
        aliases = ["one", "two"]
        doc = "colors"
        namespace = "some.name.space"


def test_enum_field():
    enum_field = EnumField("field_name", Color, Color.BLUE, metadata={"key": "value"})

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


def test_enum_field_with_type_level_default():
    class FavoriteColor(enum.Enum):
        BLUE = "Blue"
        GREEN = "Green"
        YELLOW = "Yellow"

        class Meta:
            aliases = ["one", "two"]
            doc = "favorite colors"
            namespace = "some.name.space"
            default = "Green"

    enum_field = EnumField("field_name", FavoriteColor, FavoriteColor.BLUE, metadata={"key": "value"})

    assert enum_field.get_symbols() == ["Blue", "Green", "Yellow"]
    assert enum_field._get_meta_class_attributes() == {
        "aliases": ["one", "two"],
        "doc": "favorite colors",
        "namespace": "some.name.space",
        "default": "Green",
    }
    assert enum_field.get_avro_type() == {
        "type": "enum",
        "name": "FavoriteColor",
        "symbols": ["Blue", "Green", "Yellow"],
        "aliases": ["one", "two"],
        "doc": "favorite colors",
        "namespace": "some.name.space",
        "default": "Green",
    }

    assert enum_field.get_default_value() == "Blue"


def test_enum_field_with_invalid_type_level_default():
    class FavoriteColor(enum.Enum):
        BLUE = "Blue"
        GREEN = "Green"
        YELLOW = "Yellow"

        class Meta:
            aliases = ["one", "two"]
            doc = "favorite colors"
            namespace = "some.name.space"
            default = "Red"

    enum_field = EnumField("field_name", FavoriteColor, FavoriteColor.BLUE, metadata={"key": "value"})

    with pytest.raises(ValueError, match=r"^.*Default enum symbol must be one of \['Blue', 'Green', 'Yellow'\].*$"):
        enum_field._get_meta_class_attributes()


def test_enum_field_default():
    enum_field1 = EnumField("field_name", Color, types.MissingSentinel, metadata={"key": "value"})

    enum_field2 = EnumField("field_name", Color, dataclasses.MISSING, metadata={"key": "value"})

    enum_field3 = EnumField("field_name", Color, None, metadata={"key": "value"})

    enum_field4 = EnumField("field_name", Color, Color.GREEN, metadata={"key": "value"})

    assert enum_field1.get_default_value() == dataclasses.MISSING
    assert enum_field2.get_default_value() == dataclasses.MISSING
    assert enum_field3.get_default_value() is None
    assert enum_field4.get_default_value() == "Green"
