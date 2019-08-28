import json

from dataclasses_schema_generator.schema_generator import SchemaGenerator


def test_total_schema_fields_from_class(user_dataclass):
    schema_generator = SchemaGenerator(user_dataclass)

    assert len(schema_generator.get_fields) == 2


def test_total_schema_fields_from_instance(user_dataclass):
    user = user_dataclass("test", 20)
    schema_generator = SchemaGenerator(user)

    assert len(schema_generator.get_fields) == 2


def test_schema_generator_render_from_class(user_dataclass, user_avro_json):
    user_avro_schema = SchemaGenerator(user_dataclass, include_schema_doc=False).render()

    assert json.loads(user_avro_schema) == user_avro_json


def test_schema_generator_render_from_instance(user_dataclass, user_avro_json):
    user = user_dataclass("test", 20)
    user_avro_schema = SchemaGenerator(user, include_schema_doc=False).render()

    assert json.loads(user_avro_schema) == user_avro_json


def test_schema_generator_render_from_class_with_doc(user_dataclass, user_avro_json):
    user_avro_schema = SchemaGenerator(user_dataclass).render()

    user_avro_json["doc"] = "User(name: str, age: int)"

    assert json.loads(user_avro_schema) == user_avro_json


def test_schema_generator_render_from_instance_with_doc(user_dataclass, user_avro_json):
    user = user_dataclass("test", 20)
    user_avro_schema = SchemaGenerator(user).render()

    user_avro_json["doc"] = "User(name: str, age: int)"

    assert json.loads(user_avro_schema) == user_avro_json


def test_schema_generator_class_with_list(user_advance_dataclass, user_advance_avro_json):
    user = SchemaGenerator(user_advance_dataclass, include_schema_doc=False).render()
    user_schema = json.loads(user)

    assert user_advance_avro_json == user_schema


def test_schema_documentation(user_v2_dataclass, user_v2_avro_json):
    user = SchemaGenerator(user_v2_dataclass).render()
    user_schema = json.loads(user)

    assert user_v2_avro_json == user_schema


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

        @classmethod
        def extra_avro_attributes(cls):
            return {
                "namespace": namespace,
                "aliases": aliases
            }

    user_schema_gen = SchemaGenerator(User).render()
    user_schema = json.loads(user_schema_gen)

    assert user_schema == user_extra_avro_attributes
