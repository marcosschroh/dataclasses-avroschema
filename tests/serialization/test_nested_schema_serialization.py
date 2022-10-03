import dataclasses
import typing

from dataclasses_avroschema import AvroModel


def test_one_to_one_relationship():
    """
    Test schema relationship one-to-one serialization
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
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
    expected = {"name": "john", "age": 20, "address": {"street": "test", "street_number": 10}}

    assert user.serialize() == avro_binary
    assert user.serialize(serialization_type="avro-json") == avro_json_binary

    assert User.deserialize(avro_binary, create_instance=False) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False) == expected

    assert User.deserialize(avro_binary) == user
    assert User.deserialize(avro_json_binary, serialization_type="avro-json") == user

    assert user.to_dict() == expected


def test_one_to_many_relationship():
    """
    Test schema relationship one-to-many serialization
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    address_data = {
        "street": "test",
        "street_number": 10,
    }

    address = Address(**address_data)

    data_user = {
        "name": "john",
        "age": 20,
        "addresses": [address],
    }

    user = User(**data_user)

    avro_binary = b"\x08john(\x02\x08test\x14\x00"
    avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'
    expected = {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

    assert user.serialize() == avro_binary

    # Bug in fastavro
    assert user.serialize(serialization_type="avro-json") == avro_json_binary

    assert User.deserialize(avro_binary, create_instance=False) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False) == expected

    assert User.deserialize(avro_binary) == user
    assert User.deserialize(avro_json_binary, serialization_type="avro-json") == user

    assert user.to_dict() == expected


def test_one_to_many_map_relationship():
    """
    Test schema relationship one-to-many using a map serialization
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    address_data = {
        "street": "test",
        "street_number": 10,
    }

    address = Address(**address_data)

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
    expected = {"name": "john", "age": 20, "addresses": {"main_residence": {"street": "test", "street_number": 10}}}

    assert user.serialize() == avro_binary
    assert user.serialize(serialization_type="avro-json") == avro_json_binary

    # seems that there is a bug in fastavro and raises KeyError
    assert User.deserialize(avro_binary, create_instance=False) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json", create_instance=False) == expected

    assert User.deserialize(avro_binary) == user
    # assert User.deserialize(avro_json_binary) == user

    assert user.to_dict() == expected


def test_nested_schemas_splitted() -> None:
    """
    This test will cover the cases when nested schemas are
    used in a separate way.
    """

    @dataclasses.dataclass
    class A(AvroModel):
        class Meta:
            namespace = "namespace"

    @dataclasses.dataclass
    class B(AvroModel):
        a: A

    @dataclasses.dataclass
    class C(AvroModel):
        b: B
        a: A

    b = B(a=A())
    c = C(b=B(a=A()), a=A())

    assert b.serialize() == b""
    assert c.serialize() == b""


def test_nested_schemas_splitted_with_unions() -> None:
    """
    This test will cover the cases when nested schemas with Unions that are
    used in a separate way.
    """

    @dataclasses.dataclass
    class S1(AvroModel):
        pass

    @dataclasses.dataclass
    class S2(AvroModel):
        pass

    @dataclasses.dataclass
    class A(AvroModel):
        s: typing.Union[S1, S2]

        class Meta:
            namespace = "namespace"

    @dataclasses.dataclass
    class B(AvroModel):
        a: A

    @dataclasses.dataclass
    class C(AvroModel):
        b: B
        a: A

    b = B(a=A(s=S1()))
    c = C(b=B(a=A(s=S1())), a=A(s=S1()))

    assert b.serialize() == b"\x00"
    assert c.serialize() == b"\x00\x00"


def test_nested_scheamas_splitted_with_intermediates() -> None:
    @dataclasses.dataclass
    class A(AvroModel):
        class Meta:
            namespace = "namespace"

    @dataclasses.dataclass
    class B(AvroModel):
        a: A

    @dataclasses.dataclass
    class C(AvroModel):
        a: A

    @dataclasses.dataclass
    class D(AvroModel):
        b: B
        c: C

    a = A()
    b = B(a=a)
    c = C(a=a)
    d = D(b=b, c=c)

    assert d.serialize() == b""
    assert c.serialize() == b""
