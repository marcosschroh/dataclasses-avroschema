def test_complex_fields(user_advance_dataclass):
    data = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "has_car": True,
        "favorite_colors": "GREEN",
        "md5": b"u00ff",
    }

    expected_data = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "has_car": True,
        "favorite_colors": "GREEN",
        "md5": b"u00ff",
        "country": "Argentina",
        "address": None,
    }

    data_json = {
        "name": "juan",
        "age": 20,
        "pets": ["dog"],
        "accounts": {"ing": 100},
        "has_car": True,
        "favorite_colors": "GREEN",
        "md5": "u00ff",
        "country": "Argentina",
        "address": None,
    }

    user = user_advance_dataclass(**data)

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_advance_dataclass.deserialize(avro_binary) == expected_data
    assert user_advance_dataclass.deserialize(avro_json, serialization_type="avro-json") == expected_data
    assert user.to_json() == data_json


def test_complex_fields_with_defaults(user_advance_with_defaults_dataclass):
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
        "favorite_colors": "BLUE",
        "country": "Argentina",
        "address": None,
    }

    user = user_advance_with_defaults_dataclass(**data)

    avro_binary = user.serialize()
    avro_json = user.serialize(serialization_type="avro-json")

    assert user_advance_with_defaults_dataclass.deserialize(avro_binary) == expected_data
    assert user_advance_with_defaults_dataclass.deserialize(avro_json, serialization_type="avro-json") == expected_data
    assert user.to_json() == expected_data
