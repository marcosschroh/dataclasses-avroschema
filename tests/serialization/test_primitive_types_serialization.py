from dataclasses import dataclass

from dataclasses_avroschema import AvroModel


def test_primitive_types(user_dataclass):
    data = {
        "name": "juan",
        "age": 20,
        "has_pets": True,
        "money": 100.0,
        "encoded": b"hola"
    }

    data_json = {
        "name": "juan",
        "age": 20,
        "has_pets": True,
        "money": 100.0,
        "encoded": "hola"
    }

    user = user_dataclass(**data)

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_dataclass.deserialize(avro_binary) == data
    assert user_dataclass.deserialize(avro_json, serialization_type="avro-json") == data
    assert user.to_json() == data_json


def test_primitive_types_with_defaults(user_dataclass):

    @dataclass
    class User(AvroModel):
        name: str = "Juan"
        age: int = 20
        has_pets: bool = False
        money: float = 100.0
        encoded: bytes = b"hola"

    data = {
        "name": "juan",
        "age": 20,
        "has_pets": True,
        "money": 100.0,
        "encoded": b"hola"
    }

    user = User()

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_dataclass.deserialize(avro_binary) == data
    assert user_dataclass.deserialize(avro_json, serialization_type="avro-json") == data
