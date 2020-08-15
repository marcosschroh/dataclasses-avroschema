import json
from dataclasses import dataclass

import pytest

from dataclasses_avroschema import AvroModel
from dataclasses_avroschema.schema_definition import BaseSchemaDefinition

encoded = "test".encode()


def test_total_schema_fields_from_class(user_dataclass):
    assert len(user_dataclass.get_fields()) == 5


def test_total_schema_fields_from_instance(user_dataclass):
    user = user_dataclass("test", 20, True, 10.4, encoded)

    assert len(user.get_fields()) == 5


def test_schema_render_from_class_with_field_metadata(
    user_dataclass_with_field_metadata, user_with_field_metadata_avro_json
):
    assert user_dataclass_with_field_metadata.avro_schema() == json.dumps(user_with_field_metadata_avro_json)


def test_schema_render_from_class(user_dataclass, user_avro_json):
    assert user_dataclass.avro_schema() == json.dumps(user_avro_json)


def test_schema_render_from_instance(user_dataclass, user_avro_json):
    user = user_dataclass("test", 20, True, 10.4, encoded)

    assert user.avro_schema() == json.dumps(user_avro_json)


def test_schema_render_from_class_with_doc(user_dataclass_with_doc, user_avro_json):
    user_avro_json["doc"] = "User(name: str, age: int, has_pets: bool, money: float, encoded: bytes)"

    assert user_dataclass_with_doc.avro_schema() == json.dumps(user_avro_json)


def test_schema_render_from_instance_with_doc(user_dataclass_with_doc, user_avro_json):
    user_avro_json["doc"] = "User(name: str, age: int, has_pets: bool, money: float, encoded: bytes)"
    user = user_dataclass_with_doc("test", 20, True, 10.4, encoded)

    assert user.avro_schema() == json.dumps(user_avro_json)


def test_schema_documentation(user_v2_dataclass, user_v2_avro_json):
    assert user_v2_dataclass.avro_schema() == json.dumps(user_v2_avro_json)


def test_schema_cached(user_v2_dataclass, user_v2_avro_json):
    user_schema = user_v2_dataclass.avro_schema()

    assert user_schema == json.dumps(user_v2_avro_json)
    assert user_schema == user_v2_dataclass.avro_schema()


def test_extra_avro_attributes(user_extra_avro_attributes):
    """
    This method is to test the extra avro attribute like
    namespace and aliases.
    """

    class User(AvroModel):
        "An User"
        name: str
        age: int

        class Meta:
            namespace = "test.com.ar/user/v1"
            aliases = ["User", "My favorite User"]

    assert User.avro_schema() == json.dumps(user_extra_avro_attributes)

    # test with an instance
    assert User("test", 1).avro_schema() == json.dumps(user_extra_avro_attributes)


def test_class_empty_metaclass():
    class User(AvroModel):
        "An User"
        name: str
        age: int

        class Meta:
            pass

    assert User.avro_schema()


def test_invalid_schema_type(user_dataclass):
    msg = "Invalid type. Expected avro schema type."
    with pytest.raises(ValueError, match=msg):
        user_dataclass.generate_schema(schema_type="json")


def test_not_implementd_methods():
    class Aclass:
        pass

    with pytest.raises(TypeError) as excinfo:
        BaseSchemaDefinition("avro", Aclass)

    msg = "Can't instantiate abstract class BaseSchemaDefinition with abstract methods get_rendered_fields, render"

    assert msg == str(excinfo.value)
