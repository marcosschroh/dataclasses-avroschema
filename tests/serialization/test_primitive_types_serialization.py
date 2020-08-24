from dataclasses import dataclass

from dataclasses_avroschema import AvroModel


def test_primitive_types(user_dataclass):
    data = {"name": "juan", "age": 20, "has_pets": True, "money": 100.0, "encoded": b"hola"}

    data_json = {"name": "juan", "age": 20, "has_pets": True, "money": 100.0, "encoded": "hola"}

    user = user_dataclass(**data)

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_dataclass.deserialize(avro_binary, create_instance=False) == data
    assert user_dataclass.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert user_dataclass.deserialize(avro_binary) == user
    assert user_dataclass.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_json() == data_json


def test_primitive_types_with_defaults():
    @dataclass
    class User(AvroModel):
        name: str = "marcos"
        age: int = 20
        has_pets: bool = False
        money: float = 100.0
        encoded: bytes = b"hola"

    data = {"name": "marcos", "age": 20, "has_pets": False, "money": 100.0, "encoded": b"hola"}

    data_json = {"name": "marcos", "age": 20, "has_pets": False, "money": 100.0, "encoded": "hola"}

    user = User()
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_json() == data_json


def test_primitive_types_with_nulls():
    @dataclass
    class User(AvroModel):
        name: str = None
        age: int = 20
        has_pets: bool = False
        money: float = None
        encoded: bytes = None

    data = {"name": None, "age": 20, "has_pets": False, "money": 100.0, "encoded": b"hola"}
    data_json = {"name": None, "age": 20, "has_pets": False, "money": 100.0, "encoded": "hola"}

    user = User(**data)
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_json() == data_json

    data = {"name": None, "age": 20, "has_pets": False, "money": None, "encoded": None}

    user = User()
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_json() == data
