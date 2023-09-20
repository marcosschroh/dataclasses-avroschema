import dataclasses
import enum
import json
import typing

from dataclasses_avroschema import AvroModel


def test_complex_fields(user_advance_dataclass, color_enum):
    data = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "has_car": True,
        "favorite_colors": color_enum.GREEN,
        "md5": b"u00ffffffffffffx",
    }

    expected_data = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "has_car": True,
        "favorite_colors": color_enum.GREEN,
        "md5": b"u00ffffffffffffx",
        "country": "Argentina",
        "address": None,
    }

    data_json = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "favorite_colors": color_enum.GREEN.value,
        "md5": "u00ffffffffffffx",
        "has_car": True,
        "country": "Argentina",
        "address": None,
    }

    user = user_advance_dataclass(**data)

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_advance_dataclass.deserialize(avro_binary, create_instance=False) == expected_data
    assert (
        user_advance_dataclass.deserialize(avro_json, serialization_type="avro-json", create_instance=False)
        == expected_data
    )
    assert user.to_json() == json.dumps(data_json)

    assert user_advance_dataclass.deserialize(avro_binary) == user
    assert user_advance_dataclass.deserialize(avro_json, serialization_type="avro-json") == user


def test_complex_fields_with_defaults(user_advance_with_defaults_dataclass, color_enum):
    data = {
        "name": "juan",
        "age": 20,
    }

    expected_data = {
        "name": "juan",
        "age": 20,
        "pets": ["dog", "cat"],
        "accounts": {"key": 1},
        "has_car": False,
        "favorite_colors": color_enum.BLUE,
        "country": "Argentina",
        "address": None,
    }

    expected_json = {
        "name": "juan",
        "age": 20,
        "pets": ["dog", "cat"],
        "accounts": {"key": 1},
        "has_car": False,
        "favorite_colors": color_enum.BLUE.value,
        "country": "Argentina",
        "address": None,
    }

    user = user_advance_with_defaults_dataclass(**data)
    expected_user = user_advance_with_defaults_dataclass(
        name="juan",
        age=20,
        favorite_colors=color_enum.BLUE,
    )

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_advance_with_defaults_dataclass.deserialize(avro_binary, create_instance=False) == expected_data
    assert (
        user_advance_with_defaults_dataclass.deserialize(
            avro_json, serialization_type="avro-json", create_instance=False
        )
        == expected_data
    )
    assert user.to_json() == json.dumps(expected_json)

    assert user_advance_with_defaults_dataclass.deserialize(avro_binary) == expected_user
    assert user_advance_with_defaults_dataclass.deserialize(avro_json, serialization_type="avro-json") == expected_user

    # check that is possible to continue doing serialization and dedesialization operations
    expected_user.favorite_colors = "YELLOW"
    assert expected_user.serialize() == b"\x08juan(\x04\x06dog\x06cat\x00\x02\x06key\x02\x00\x00\x02\x12Argentina\x00"
    assert user.avro_schema() == expected_user.avro_schema()


def test_complex_fields_with_enum(user_advance_dataclass_with_enum, color_enum):
    data = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "has_car": True,
        "favorite_colors": color_enum.GREEN,
        "md5": b"u00ffffffffffffx",
    }

    expected_data = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "has_car": True,
        "favorite_colors": color_enum.GREEN,
        "md5": b"u00ffffffffffffx",
        "country": "Argentina",
        "address": None,
        "user_type": None,
    }

    data_json = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "favorite_colors": "GREEN",
        "md5": "u00ffffffffffffx",
        "has_car": True,
        "country": "Argentina",
        "address": None,
        "user_type": None,
    }

    user = user_advance_dataclass_with_enum(**data)

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_advance_dataclass_with_enum.deserialize(avro_binary, create_instance=False) == expected_data
    assert (
        user_advance_dataclass_with_enum.deserialize(avro_json, serialization_type="avro-json", create_instance=False)
        == expected_data
    )
    assert user.to_json() == json.dumps(data_json)

    assert user_advance_dataclass_with_enum.deserialize(avro_binary) == user
    assert user_advance_dataclass_with_enum.deserialize(avro_json, serialization_type="avro-json") == user


def test_complex_fields_with_defaults_with_enum(user_advance_with_defaults_dataclass_with_enum, color_enum):
    data = {
        "name": "juan",
        "age": 20,
    }

    expected_data = {
        "name": "juan",
        "age": 20,
        "pets": ["dog", "cat"],
        "accounts": {"key": 1},
        "has_car": False,
        "favorite_colors": color_enum.BLUE,
        "country": "Argentina",
        "address": None,
        "user_type": None,
    }

    data_json = {
        "name": "juan",
        "age": 20,
        "pets": ["dog", "cat"],
        "accounts": {"key": 1},
        "has_car": False,
        "favorite_colors": color_enum.BLUE.value,
        "country": "Argentina",
        "address": None,
        "user_type": None,
    }

    user = user_advance_with_defaults_dataclass_with_enum(**data)
    expected_user = user_advance_with_defaults_dataclass_with_enum(
        name="juan",
        age=20,
        favorite_colors=color_enum.BLUE,
    )

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert (
        user_advance_with_defaults_dataclass_with_enum.deserialize(avro_binary, create_instance=False) == expected_data
    )
    assert (
        user_advance_with_defaults_dataclass_with_enum.deserialize(
            avro_json, serialization_type="avro-json", create_instance=False
        )
        == expected_data
    )
    assert user.to_json() == json.dumps(data_json)

    assert user_advance_with_defaults_dataclass_with_enum.deserialize(avro_binary) == expected_user
    assert (
        user_advance_with_defaults_dataclass_with_enum.deserialize(avro_json, serialization_type="avro-json")
        == expected_user
    )

    # check that is possible to continue doing serialization and dedesialization operations
    expected_user.favorite_colors = color_enum.YELLOW
    assert (
        expected_user.serialize() == b"\x08juan(\x04\x06dog\x06cat\x00\x02\x06key\x02\x00\x00\x02\x12Argentina\x00\x00"
    )
    assert user.avro_schema() == expected_user.avro_schema()


def test_enum_fields_with_inner_schema():
    class InnerEnum(enum.Enum):
        ONE = "One"
        TWO = "Two"

    class OuterEnum(enum.Enum):
        THREE = "Three"
        FOUR = "Four"

    @dataclasses.dataclass
    class InnerSchema(AvroModel):
        """Inner schema"""

        some_val: str
        enum_field1: InnerEnum

    @dataclasses.dataclass
    class OuterSchema(AvroModel):
        """Outer schema"""

        some_val2: str
        enum_field2: OuterEnum
        inner_schema: InnerSchema

    example = OuterSchema(
        some_val2="val2",
        enum_field2=OuterEnum.FOUR,
        inner_schema=InnerSchema(some_val="val1", enum_field1=InnerEnum.TWO),
    )

    expected_data = {
        "some_val2": "val2",
        "enum_field2": OuterEnum.FOUR,
        "inner_schema": {"some_val": "val1", "enum_field1": InnerEnum.TWO},
    }

    expected_json = {
        "some_val2": "val2",
        "enum_field2": "Four",
        "inner_schema": {"some_val": "val1", "enum_field1": "Two"},
    }

    avro_binary = example.serialize()
    avro_json = example.serialize(serialization_type="avro-json")

    assert OuterSchema.deserialize(avro_binary, create_instance=False) == expected_data
    assert OuterSchema.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == expected_data
    assert example.to_json() == json.dumps(expected_json)

    assert OuterSchema.deserialize(avro_binary) == example
    assert OuterSchema.deserialize(avro_json, serialization_type="avro-json") == example


def test_literal_enum():
    class TestEnum(enum.Enum):
        ONE = "one"
        TWO = "two"

    @dataclasses.dataclass
    class NestedTestModel(AvroModel):
        literal: typing.Literal[TestEnum.TWO]

    @dataclasses.dataclass
    class TestModel(AvroModel):
        literal: typing.Literal[TestEnum.ONE]
        nested: NestedTestModel

    example = TestModel(literal=TestEnum.ONE, nested=NestedTestModel(literal=TestEnum.TWO))
    expected_data = {"literal": TestEnum.ONE, "nested": {"literal": TestEnum.TWO}}
    expected_json = json.dumps({"literal": TestEnum.ONE.value, "nested": {"literal": TestEnum.TWO.value}})

    avro_binary = example.serialize()
    avro_json = example.serialize(serialization_type="avro-json")

    assert TestModel.deserialize(avro_binary, create_instance=False) == expected_data
    assert TestModel.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == expected_data

    assert example.to_json() == expected_json

    assert TestModel.deserialize(avro_binary) == example
    assert TestModel.deserialize(avro_json, serialization_type="avro-json") == example


def test_literal_fields():
    class TestEnum(enum.Enum):
        ONE = "one"
        TWO = "two"

    @dataclasses.dataclass
    class NestedTestModel(AvroModel):
        single_literal_2: typing.Literal[TestEnum.TWO]
        multi_literal_2: typing.Literal["2", 2, False, b"two", TestEnum.TWO]

    @dataclasses.dataclass
    class TestModel(AvroModel):
        single_literal_1: typing.Literal["1st_literal"]
        multi_literal_1: typing.Literal["1", 1, True, b"one", TestEnum.ONE]
        nested_model: NestedTestModel

    example = TestModel(
        single_literal_1="1st_literal",
        multi_literal_1=b"one",
        nested_model=NestedTestModel(
            single_literal_2=TestEnum.TWO,
            multi_literal_2=2,
        ),
    )

    expected_data = {
        "single_literal_1": "1st_literal",
        "multi_literal_1": b"one",
        "nested_model": {
            "single_literal_2": TestEnum.TWO,
            "multi_literal_2": 2,
        },
    }
    expected_json = json.dumps(
        {
            "single_literal_1": "1st_literal",
            "multi_literal_1": "one",
            "nested_model": {
                "single_literal_2": TestEnum.TWO.value,
                "multi_literal_2": 2,
            },
        }
    )

    avro_binary = example.serialize()
    avro_json = example.serialize(serialization_type="avro-json")

    assert TestModel.deserialize(avro_binary, create_instance=False) == expected_data
    assert TestModel.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == expected_data

    assert example.to_json() == expected_json, f"\nexpected:\n{expected_json}\nactual:\n{example.to_json()}\n"

    assert TestModel.deserialize(avro_binary) == example
    assert TestModel.deserialize(avro_json, serialization_type="avro-json") == example
