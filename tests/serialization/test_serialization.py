import datetime
import uuid

import typing
from dataclasses import dataclass

import pytest

from dataclasses_avroschema import AvroModel, types


a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)


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


address_data = {
    "street": "test",
    "street_number": 10,
}

data_user = {
    "name": "john",
    "age": 20,
    "addresses": [Address(**address_data)],
}

user_avro_binary = b"\x08john(\x02\x08test\x14\x00"
user_avro_json = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'
user_json = {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}


@dataclass
class UserAdvance(AvroModel):
    name: str
    age: int
    is_developer: bool
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    has_car: bool = False
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"])
    favorite_language: types.Enum = types.Enum(["PYTHON", "JAVA", "JS"], default="JS")
    country: str = "Argentina"
    years_of_expirience: int = 5
    md5: types.Fixed = types.Fixed(16)
    birthday: datetime.date = a_datetime.date()
    meeting_time: datetime.time = a_datetime.time()
    release_datetime: datetime.datetime = a_datetime
    event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"


advance_data = {
    "name": "juan",
    "age": 20,
    "is_developer": True,
    "pets": ["dog", "cat"],
    "accounts": {"ing": 100},
    "favorite_colors": "GREEN",
    "favorite_language": "JS",
    "md5": b"\u00ff",
}

advance_user_json = {
    "name": "juan",
    "age": 20,
    "is_developer": True,
    "pets": ["dog", "cat"],
    "accounts": {"ing": 100},
    "has_car": {"boolean": False},
    "favorite_colors": "GREEN",
    "favorite_language": "JS",
    "country": {"string": "Argentina"},
    "years_of_expirience": {"int": 5},
    "md5": "\\u00ff",
    "birthday": 18181,
    "meeting_time": 64662000,
    "release_datetime": 1570895862000,
    "event_uuid": "09f00184-7721-4266-a955-21048a5cc235"
}

advance_user_avro_binary = b'\x08juan(\x01\x04\x06dog\x06cat\x00\x02\x06ing\xc8\x01\x00\x00\x00\x04\x04\x00\x12Argentina\x00\n\\u00ff\x8a\x9c\x02\xe0\xa7\xd5=\xe0\xe3\x84\x8b\xb8[H09f00184-7721-4266-a955-21048a5cc235'
advance_user_avro_json = b'{"name": "juan", "age": 20, "is_developer": true, "pets": ["dog", "cat"], "accounts": {"ing": 100}, "has_car": {"boolean": false}, "favorite_colors": "GREEN", "favorite_language": "JS", "country": {"string": "Argentina"}, "years_of_expirience": {"int": 5}, "md5": "\\\\u00ff", "birthday": 18181, "meeting_time": 64662000, "release_datetime": 1570895862000, "event_uuid": "09f00184-7721-4266-a955-21048a5cc235"}'

CLASSES_DATA_BINARY = (
    # (User, data_user, user_avro_binary, user_avro_json, user_json),
    (UserAdvance, advance_data, advance_user_avro_binary, advance_user_avro_json, advance_user_json),
)


@pytest.mark.parametrize("klass, data, avro_binary, avro_json, instance_json", CLASSES_DATA_BINARY)
def test_serialization(klass, data, avro_binary, avro_json, instance_json):
    instance = klass(**data)

    assert instance.serialize() == avro_binary
    assert instance.serialize(serialization_type="avro-json") == avro_json


@pytest.mark.parametrize("klass, data, avro_binary, avro_json, instance_json", CLASSES_DATA_BINARY)
def test_deserialization(klass, data, avro_binary, avro_json, instance_json):
    instance = klass(**data)

    assert instance.deserialize(avro_binary, create_instance=False) == instance_json
    # assert instance.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == instance_json

    # assert instance.deserialize(avro_binary) == instance
    # assert instance.deserialize(avro_json, serialization_type="avro-json") == instance


# @pytest.mark.parametrize("klass, data, avro_binary, avro_json, instance_json", CLASSES_DATA_BINARY)
# def test_deserialization_with_class(klass, data, avro_binary, avro_json, instance_json):
#     instance = klass(**data)

#     assert klass.deserialize(avro_binary, create_instance=False) == instance_json
#     assert klass.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == instance_json

#     assert klass.deserialize(avro_binary) == instance
#     assert klass.deserialize(avro_json, serialization_type="avro-json") == instance


@pytest.mark.parametrize("klass, data, avro_binary, avro_json, instance_json", CLASSES_DATA_BINARY)
def test_to_json(klass, data, avro_binary, avro_json, instance_json):
    instance = klass(**data)

    assert instance.to_json() == instance_json


def test_invalid_serialization_deserialization_types():
    user = User(**data_user)

    with pytest.raises(ValueError):
        user.serialize(serialization_type="json")

    with pytest.raises(ValueError):
        user.deserialize(b"", serialization_type="json")