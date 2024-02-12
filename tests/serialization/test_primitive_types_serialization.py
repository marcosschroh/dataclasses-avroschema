import dataclasses
import json
import math

from dataclasses_avroschema import AvroModel, types


def test_primitive_types(user_dataclass):
    data = {
        "name": "juan",
        "age": 20,
        "has_pets": True,
        "money": 100.0,
        "encoded": b"hola",
    }

    data_json = {
        "name": "juan",
        "age": 20,
        "has_pets": True,
        "money": 100.0,
        "encoded": "hola",
    }

    user = user_dataclass(**data)

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_dataclass.deserialize(avro_binary, create_instance=False) == data
    assert user_dataclass.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert user_dataclass.deserialize(avro_binary) == user
    assert user_dataclass.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_json() == json.dumps(data_json)


def test_primitive_types_with_defaults():
    @dataclasses.dataclass
    class User(AvroModel):
        name: str = "marcos"
        age: int = 20
        has_pets: bool = False
        money: float = 100.0
        encoded: bytes = b"hola"
        height: types.Int32 = 184

    data = {
        "name": "marcos",
        "age": 20,
        "has_pets": False,
        "money": 100.0,
        "encoded": b"hola",
        "height": 184,
    }
    data_json = {
        "name": "marcos",
        "age": 20,
        "has_pets": False,
        "money": 100.0,
        "encoded": "hola",
        "height": 184,
    }

    user = User()
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data_json)

    # check that works with schema evolution
    user = User(name="Juan", age=30)
    avro_json = user.serialize(serialization_type="avro-json")

    data = {
        "name": "Juan",
        "age": 30,
        "has_pets": False,
        "money": 100.0,
        "encoded": b"hola",
        "height": 184,
    }
    data_json = {
        "name": "Juan",
        "age": 30,
        "has_pets": False,
        "money": 100.0,
        "encoded": "hola",
        "height": 184,
    }

    # assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    # assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user
    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data_json)


def test_primitive_types_with_nulls():
    @dataclasses.dataclass
    class User(AvroModel):
        name: str = None
        age: int = 20
        has_pets: bool = False
        money: float = None
        encoded: bytes = None
        height: types.Int32 = None

    data = {
        "name": None,
        "age": 20,
        "has_pets": False,
        "money": 100.0,
        "encoded": b"hola",
        "height": 184,
    }
    data_json = {
        "name": None,
        "age": 20,
        "has_pets": False,
        "money": 100.0,
        "encoded": "hola",
        "height": 184,
    }

    user = User(**data)
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data

    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data_json)

    data = {
        "name": None,
        "age": 20,
        "has_pets": False,
        "money": None,
        "encoded": None,
        "height": None,
    }

    user = User()
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
    assert user.to_json() == json.dumps(data)


def test_float32_primitive_type():
    @dataclasses.dataclass
    class User(AvroModel):
        height: types.Float32 = None

    data = {"height": 178.3}

    user = User(**data)
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    # Floating point error expected
    res = user.deserialize(avro_binary, create_instance=False)
    assert res["height"] != data["height"]
    assert math.isclose(res["height"], data["height"], abs_tol=1e-5)

    res = user.deserialize(avro_json, serialization_type="avro-json", create_instance=False)
    assert res["height"] == data["height"]

    # Floating point error expected
    res = user.deserialize(avro_binary)
    assert res.height != user.height
    assert math.isclose(res.height, user.height, abs_tol=1e-5)

    res = user.deserialize(avro_json, serialization_type="avro-json")
    assert res.height == user.height

    res = user.to_dict()
    assert res["height"] == data["height"]

    data = {"height": None}

    user = User()
    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user.deserialize(avro_binary, create_instance=False) == data
    assert user.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == data
    assert user.deserialize(avro_binary) == user
    assert user.deserialize(avro_json, serialization_type="avro-json") == user

    assert user.to_dict() == data
