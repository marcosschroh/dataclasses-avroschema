import json
import pytest
import typing
import dataclasses

from dataclasses_avroschema.schema_generator import SchemaGenerator

encoded = "test".encode()


def test_total_schema_fields_from_class(user_dataclass):
    schema_generator = SchemaGenerator(user_dataclass)

    assert len(schema_generator.get_fields) == 5


def test_total_schema_fields_from_instance(user_dataclass):
    user = user_dataclass("test", 20, True, 10.4, encoded)
    schema_generator = SchemaGenerator(user)

    assert len(schema_generator.get_fields) == 5


def test_schema_render_from_class(user_dataclass, user_avro_json):
    user_schema = SchemaGenerator(user_dataclass, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_avro_json)


def test_schema_render_from_instance(user_dataclass, user_avro_json):
    user = user_dataclass("test", 20, True, 10.4, encoded)
    user_schema = SchemaGenerator(user, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_avro_json)


def test_schema_render_from_class_with_doc(user_dataclass, user_avro_json):
    user_avro_json["doc"] = "User(name: str, age: int, has_pets: bool, money: float, encoded: bytes)"
    user_schema = SchemaGenerator(user_dataclass).avro_schema()

    assert user_schema == json.dumps(user_avro_json)


def test_schema_render_from_instance_with_doc(user_dataclass, user_avro_json):
    user_avro_json["doc"] = "User(name: str, age: int, has_pets: bool, money: float, encoded: bytes)"

    user = user_dataclass("test", 20, True, 10.4, encoded)
    user_schema = SchemaGenerator(user).avro_schema()

    assert user_schema == json.dumps(user_avro_json)


def test_schema_with_complex_types(user_advance_dataclass, user_advance_avro_json):
    user_schema = SchemaGenerator(user_advance_dataclass, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_advance_avro_json)


def test_schema_with_complex_types_and_defaults(user_advance_with_defaults_dataclass, user_advance_with_defaults_avro_json):
    user_schema = SchemaGenerator(
        user_advance_with_defaults_dataclass,
        include_schema_doc=False
    ).avro_schema()

    assert user_schema == json.dumps(user_advance_with_defaults_avro_json)


def test_schema_documentation(user_v2_dataclass, user_v2_avro_json):
    user_schema = SchemaGenerator(user_v2_dataclass).avro_schema()

    assert user_schema == json.dumps(user_v2_avro_json)


def test_extra_avro_attributes(user_extra_avro_attributes):
    """
    This method is to test the extra avro attribute like
    namespace and aliases.
    """
    namespace = "test.com.ar/user/v1"
    aliases = ["User", "My favorite User"]

    class User:
        "An User"
        name: str
        age: int

        @staticmethod
        def extra_avro_attributes():
            return {
                "namespace": namespace,
                "aliases": aliases
            }

    user_schema = SchemaGenerator(User).avro_schema()
    assert user_schema == json.dumps(user_extra_avro_attributes)

    # test with an instance
    user_schema = SchemaGenerator(User("test", 1)).avro_schema()
    assert user_schema == json.dumps(user_extra_avro_attributes)


def test_extra_avro_attributes_invalid(user_extra_avro_attributes):
    """
    This method is to test the extra avro attribute like
    namespace and aliases.
    """
    class User:
        "An User"
        name: str
        age: int

        @staticmethod
        def extra_avro_attributes():
            return None

    msg = "Dict must be returned type in extra_avro_attributes method"
    with pytest.raises(AssertionError, match=msg):
        SchemaGenerator(User).avro_schema()


def test_invalid_schema_type(user_dataclass):
    msg = "Invalid type. Expected avro schema type."
    with pytest.raises(ValueError, match=msg):
        SchemaGenerator(user_dataclass).generate_schema(schema_type="json")


def test_schema_with_unions_type(union_type_schema):
    class Bus:
        "A Bus"
        engine_name: str

    class Car:
        "A Car"
        engine_name: str

    class UnionSchema:
        "Some Unions"
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Union[Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(
            default_factory=lambda: {"engine_name": "honda"})

    schema = SchemaGenerator(UnionSchema).avro_schema()
    assert schema == json.dumps(union_type_schema)
