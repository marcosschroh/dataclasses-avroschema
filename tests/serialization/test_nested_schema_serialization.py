import dataclasses
import datetime
import typing

import pytest

from dataclasses_avroschema import AvroModel
from dataclasses_avroschema.faust import AvroRecord
from dataclasses_avroschema.pydantic import AvroBaseModel
from dataclasses_avroschema.pydantic.v1 import AvroBaseModel as AvroBaseModelV1

parametrize_base_model = pytest.mark.parametrize(
    "model_class, decorator",
    [
        (AvroModel, dataclasses.dataclass),
        (AvroBaseModel, lambda f: f),
        (AvroBaseModelV1, lambda f: f),
        (AvroRecord, dataclasses.dataclass),
    ],
)


@parametrize_base_model
def test_one_to_one_relationship(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    """
    Test schema relationship one-to-one serialization
    """

    @decorator
    class Address(model_class):
        "An Address"

        street: str
        street_number: int

    @decorator
    class User(model_class):
        "An User with Address"

        name: str
        age: int
        address: Address

    address_data = {
        "street": "test",
        "street_number": 10,
    }

    address = Address(**address_data)

    data_user = {
        "name": "john",
        "age": 20,
        "address": address,
    }

    user = User(**data_user)

    avro_binary = b"\x08john(\x08test\x14"
    avro_json_binary = b'{"name": "john", "age": 20, "address": {"street": "test", "street_number": 10}}'
    expected = {
        "name": "john",
        "age": 20,
        "address": {"street": "test", "street_number": 10},
    }

    assert user.serialize() == avro_binary
    assert user.serialize(serialization_type="avro-json") == avro_json_binary

    assert User.deserialize(avro_binary, create_instance=False) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False) == expected

    assert User.deserialize(avro_binary) == user
    assert User.deserialize(avro_json_binary, serialization_type="avro-json") == user

    assert user.to_dict() == expected


@parametrize_base_model
def test_one_to_many_relationship(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    """
    Test schema relationship one-to-many serialization
    """

    @decorator
    class Address(model_class):
        "An Address"

        street: str
        street_number: int
        created_at: datetime.datetime

    @decorator
    class User(model_class):
        "User with multiple Address"

        name: str
        age: int
        addresses: typing.List[Address]
        addresses_as_tuple: typing.Tuple[Address, ...]

    created_at = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)
    address_data = {"street": "test", "street_number": 10, "created_at": created_at}

    address = Address(**address_data)
    second_address = Address(**address_data)

    data_user = {
        "name": "john",
        "age": 20,
        "addresses": [address],
        "addresses_as_tuple": (
            address,
            second_address,
        ),
    }

    user = User(**data_user)

    avro_binary = b"\x08john(\x02\x08test\x14\xe0\xd7\xf3\x91\xb8[\x00\x04\x08test\x14\xe0\xd7\xf3\x91\xb8[\x08test\x14\xe0\xd7\xf3\x91\xb8[\x00"  # noqa
    avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10, "created_at": 1570903062000}], "addresses_as_tuple": [{"street": "test", "street_number": 10, "created_at": 1570903062000}, {"street": "test", "street_number": 10, "created_at": 1570903062000}]}'  # noqa
    expected = {
        "name": "john",
        "age": 20,
        "addresses": [{"street": "test", "street_number": 10, "created_at": created_at}],
        "addresses_as_tuple": (
            {"street": "test", "street_number": 10, "created_at": created_at},
            {"street": "test", "street_number": 10, "created_at": created_at},
        ),
    }

    assert user.serialize() == avro_binary
    assert user.serialize(serialization_type="avro-json") == avro_json_binary

    assert User.deserialize(avro_binary, create_instance=False) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False) == expected

    assert User.deserialize(avro_binary) == user
    assert User.deserialize(avro_json_binary, serialization_type="avro-json") == user

    assert user.to_dict() == expected
    assert user.to_json()


@parametrize_base_model
def test_one_to_many_map_relationship(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    """
    Test schema relationship one-to-many using a map serialization
    """

    @decorator
    class Address(model_class):
        "An Address"

        street: str
        street_number: int

    @decorator
    class User(model_class):
        "User with multiple Address"

        name: str
        age: int
        addresses: typing.Dict[str, Address]

    address_data = {
        "street": "test",
        "street_number": 10,
    }

    address = Address.parse_obj(address_data)

    data_user = {
        "name": "john",
        "age": 20,
        "addresses": {"main_residence": address},
    }

    user = User(**data_user)

    avro_binary = b"\x08john(\x02\x1cmain_residence\x08test\x14\x00"
    avro_json_binary = (
        b'{"name": "john", "age": 20, "addresses": {"main_residence": {"street": "test", "street_number": 10}}}'
    )
    expected = {
        "name": "john",
        "age": 20,
        "addresses": {"main_residence": {"street": "test", "street_number": 10}},
    }

    assert user.serialize() == avro_binary
    assert user.serialize(serialization_type="avro-json") == avro_json_binary

    # seems that there is a bug in fastavro and raises KeyError
    assert User.deserialize(avro_binary, create_instance=False) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False) == expected

    assert User.deserialize(avro_binary) == user
    # assert User.deserialize(avro_json_binary) == user

    assert user.to_dict() == expected


@parametrize_base_model
def test_nested_schemas_splitted(model_class: typing.Type[AvroModel], decorator: typing.Callable) -> None:
    """
    This test will cover the cases when nested schemas are
    used in a separate way.
    """

    @decorator
    class A(model_class):
        class Meta:
            namespace = "namespace"

    @decorator
    class B(model_class):
        a: A

    @decorator
    class C(model_class):
        b: B
        a: A

    b = B(a=A())
    c = C(b=B(a=A()), a=A())

    assert b.serialize() == b""
    assert c.serialize() == b""


@parametrize_base_model
def test_nested_schemas_splitted_with_intermediates(
    model_class: typing.Type[AvroModel], decorator: typing.Callable
) -> None:
    @decorator
    class A(model_class):
        class Meta:
            namespace = "namespace"

    @decorator
    class B(model_class):
        a: A

    @decorator
    class C(model_class):
        a: A

    @decorator
    class D(model_class):
        b: B
        c: C

    a = A()
    b = B(a=a)
    c = C(a=a)
    d = D(b=b, c=c)

    assert d.serialize() == b""
    assert c.serialize() == b""


@parametrize_base_model
def test_nested_schemas_splitted_with_unions(model_class: typing.Type[AvroModel], decorator: typing.Callable) -> None:
    """
    This test will cover the cases when nested schemas with Unions that are
    used in a separate way.
    """
    if model_class == AvroBaseModelV1:
        pytest.skip(reason="Smart Unions are not supported properly in `AvroBaseModelV1` (pydantic v1)")

    @decorator
    class S1(model_class):
        ...

        class Meta:
            namespace = "my_namespace"

    @decorator
    class S2(model_class):
        age: int = 10

    @decorator
    class A(model_class):
        s: typing.Union[S1, S2]

    @decorator
    class D(model_class):
        name: str = ""

    @decorator
    class B(model_class):
        a: typing.Union[A, D]

    @decorator
    class C(model_class):
        b: B
        a: A

    b = B(a=A(s=S1()))
    c = C(b=B(a=A(s=S1())), a=A(s=S1()))
    c2 = C(b=B(a=A(s=S1())), a=A(s=S2()))

    ser = b.serialize()
    assert ser == b"\x00\x00"
    assert B.deserialize(ser) == b

    ser = c.serialize()
    assert ser == b"\x00\x00\x00"
    assert C.deserialize(ser) == c

    ser = c2.serialize()
    assert ser == b"\x00\x00\x02\x14"
    assert C.deserialize(ser) == c2


@parametrize_base_model
def test_nested_several_layers(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    @decorator
    class Friend(model_class):
        name: str
        hobbies: typing.List[str]

    @decorator
    class User(model_class):
        name: str
        friends: typing.List[Friend]

    user = User(name="Alex", friends=[Friend(name="Mr. Robot", hobbies=["fishing", "codding"])])
    assert User.deserialize(user.serialize()) == user


@parametrize_base_model
def test_union_with_multiple_records(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    @decorator
    class EventOne(model_class):
        name: str
        tag: typing.Literal["EventOne"] = "EventOne"

    @decorator
    class EventTwo(model_class):
        name: str
        tag: typing.Literal["EventTwo"] = "EventTwo"

    @decorator
    class EventManager(model_class):
        event: typing.Union[EventOne, EventTwo]
        capacity: int = 100

    # check union with first element
    event = EventManager(event=EventOne(name="hello Event one"))
    event_serialized = event.serialize()

    assert event_serialized == b"\x00\x1ehello Event one\x10EventOne\xc8\x01"
    assert EventManager.deserialize(event_serialized) == event

    # check union with second element
    event = EventManager(event=EventTwo(name="hello Event two"), capacity=150)
    event_serialized = event.serialize()

    assert event_serialized == b"\x02\x1ehello Event two\x10EventTwo\xac\x02"
    assert EventManager.deserialize(event_serialized) == event


@parametrize_base_model
def test_inheritance(model_class: typing.Type[AvroModel], decorator: typing.Callable) -> None:
    @decorator
    class A(model_class):
        a: int

    @decorator
    class Parent(model_class):
        p: A

    @decorator
    class Child(Parent):
        c: int

    child = Child(p=A(a=1), c=1)
    ser = child.serialize()
    assert Child.deserialize(ser) == child
