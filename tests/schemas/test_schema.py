import json
import typing
from dataclasses import dataclass

import pytest
from fastavro.validation import ValidationError

from dataclasses_avroschema import AvroModel
from dataclasses_avroschema.schema_definition import BaseSchemaDefinition
from dataclasses_avroschema.types import JsonDict

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
    user_avro_json["doc"] = "I am documented."

    assert user_dataclass_with_doc.avro_schema() == json.dumps(user_avro_json)


def test_schema_render_from_instance_with_doc(user_dataclass_with_doc, user_avro_json):
    user_avro_json["doc"] = "I am documented."
    user = user_dataclass_with_doc("test", 20, True, 10.4, encoded)

    assert user.avro_schema() == json.dumps(user_avro_json)


def test_schema_doc_from_meta():
    documentation = "MyClass documentation from Meta"

    @dataclass
    class MyClass(AvroModel):
        field_1: str

        class Meta:
            schema_doc = documentation

    schema = MyClass.avro_schema_to_python()
    assert schema["doc"] == documentation


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


def test_inherit_dataclass_missing_docs():
    @dataclass
    class BaseUser:
        id: int

    class User(AvroModel, BaseUser):
        age: int

    assert User.avro_schema()


def test_get_fields():
    class Child(AvroModel):
        name: str

    class Parent(AvroModel):
        children: typing.List[Child]

    assert Parent.get_fields()[0].internal_field
    assert Parent.avro_schema()
    assert Parent.fake()


def test_schema_name_from_relationship():
    @dataclass
    class MyClass(AvroModel):
        field_1: str

        class Meta:
            schema_name = "custom_class"

    class MySecondClass(AvroModel):
        field_2: MyClass

        class Meta:
            schema_name = "custom_name"

    schema = MySecondClass.avro_schema_to_python()
    assert schema["fields"][0]["type"]["name"] == "custom_class"


def test_alias_from_relationship():
    @dataclass
    class MyClass(AvroModel):
        name: str

    @dataclass
    class MySecondClass(AvroModel):
        inner_ref: MyClass
        inner_ref_2: MyClass

        class Meta:
            alias_nested_items = {"inner_ref_2": "inner_ref_2"}

    schema = MySecondClass.avro_schema_to_python()
    for i, typename in enumerate(["inner_ref", "inner_ref_2"]):
        assert schema["fields"][i]["name"] == typename
        assert schema["fields"][i]["type"]["fields"] == [{"name": "name", "type": "string"}]


def test_order_field(order_fields_schema):
    @dataclass
    class User(AvroModel):
        name: str
        age: int
        money: float
        encoded: bytes
        has_pets: bool = False

        class Meta:
            field_order = [
                "encoded",
                "has_pets",
                "money",
                "name",
                "age",
            ]

    assert User.avro_schema() == json.dumps(order_fields_schema)


def test_order_field_not_specifing_all(order_fields_schema):
    @dataclass
    class User(AvroModel):
        name: str
        age: int
        money: float
        encoded: bytes
        has_pets: bool = False

        class Meta:
            field_order = [
                "encoded",
                "has_pets",
                "money",
            ]

    assert User.avro_schema() == json.dumps(order_fields_schema)


def test_validate():
    @dataclass
    class User(AvroModel):
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

    user_instance = User.fake()
    assert user_instance.validate()

    # set 1 to the name attribute and the fastavro validation should fail
    # This is possible because in dataclasses there is not restriction,
    # but at the moment of using pydantic this will change
    user_instance.name = 1
    with pytest.raises(ValidationError) as exc:
        assert user_instance.validate()

    assert json.loads(str(exc.value)) == ["User.name is <1> of type <class 'int'> expected string"]


def test_parse_obj():
    """
    Created nested schema resolution directly from dictionaries
    """

    @dataclass
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    @dataclass
    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    data_user = {
        "name": "john",
        "age": 20,
        "addresses": [
            {
                "street": "test",
                "street_number": 10,
            }
        ],
    }
    user = User.parse_obj(data=data_user)
    assert type(user.addresses[0]) is Address
    assert User.avro_schema()


def test_avro_schema_to_python_method_with_inheritance(user_avro_json: JsonDict) -> None:
    @dataclass
    class Parent(AvroModel):
        name: str
        age: int

    @dataclass
    class Child(Parent):
        has_pets: bool
        money: float
        encoded: bytes

    @dataclass
    class Child2(Parent, AvroModel):
        has_pets: bool
        money: float
        encoded: bytes

    child_schema = Child.avro_schema_to_python()
    child_2_schema = Child2.avro_schema_to_python()

    assert child_schema["fields"] == child_2_schema["fields"] == user_avro_json["fields"]


def test_avro_schema_method_with_inheritance() -> None:
    @dataclass
    class Common(AvroModel):
        """Common docs"""

        some_data: str

    @dataclass
    class DerivedA(Common):
        """DerivedA docs"""

        some_more_data_A: str

    @dataclass
    class DerivedB(Common):
        """DerivedB docs"""

        some_more_data_B: str

    common_schema = Common.avro_schema()
    derived_a_schema = DerivedA.avro_schema()
    derived_b_schema = DerivedB.avro_schema()

    assert (
        common_schema
        == '{"type": "record", "name": "Common", "fields": [{"name": "some_data", "type": "string"}], "doc": "Common docs"}'
    )
    assert (
        derived_a_schema
        == '{"type": "record", "name": "DerivedA", "fields": [{"name": "some_data", "type": "string"}, {"name": "some_more_data_A", "type": "string"}], "doc": "DerivedA docs"}'
    )
    assert (
        derived_b_schema
        == '{"type": "record", "name": "DerivedB", "fields": [{"name": "some_data", "type": "string"}, {"name": "some_more_data_B", "type": "string"}], "doc": "DerivedB docs"}'
    )
