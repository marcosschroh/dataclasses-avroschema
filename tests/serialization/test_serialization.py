import datetime
import enum
import typing
import uuid
from dataclasses import dataclass

import pytest
from dateutil.tz import UTC

from dataclasses_avroschema import AVRO, AVRO_JSON, AvroModel
from dataclasses_avroschema.types import SerializationType

a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=UTC)


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


@dataclass
class UserCompatible(AvroModel):
    "User with multiple Address"

    name: str
    age: int
    addresses: typing.List[Address]
    nickname: typing.Optional[str] = None

    class Meta:
        schema_name = "User"


address_data = {
    "street": "test",
    "street_number": 10,
}

data_user = {
    "name": "john",
    "age": 20,
    "addresses": [Address.parse_obj(address_data)],
}

user_avro_binary = b"\x08john(\x02\x08test\x14\x00"
user_avro_json = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'
user_json = {
    "name": "john",
    "age": 20,
    "addresses": [{"street": "test", "street_number": 10}],
}


class FavoriteColor(str, enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class FavoriteLanguage(str, enum.Enum):
    PYTHON = "PYTHON"
    JAVA = "JAVA"
    JS = "JS"


@dataclass
class UserAdvance(AvroModel):
    name: str
    age: int
    is_developer: bool
    pets: typing.List[str]
    accounts: typing.Dict[str, int]
    favorite_colors: FavoriteColor
    favorite_language: FavoriteLanguage = FavoriteLanguage.JS
    has_car: bool = False
    country: str = "Argentina"
    years_of_expirience: int = 5
    md5: bytes = b"u00ff"
    # md5: types.Fixed = types.Fixed(16)
    birthday: datetime.date = a_datetime.date()
    meeting_time: datetime.time = a_datetime.time()
    release_datetime: datetime.datetime = a_datetime
    event_uuid: uuid.UUID = uuid.UUID("09f00184-7721-4266-a955-21048a5cc235")


advance_data = {
    "name": "juan",
    "age": 20,
    "is_developer": True,
    "pets": ["dog", "cat"],
    "accounts": {"ing": 100},
    "favorite_colors": FavoriteColor.GREEN,
    "favorite_language": FavoriteLanguage.JS,
}

advance_user_json = {
    "name": "juan",
    "age": 20,
    "is_developer": True,
    "pets": ["dog", "cat"],
    "accounts": {"ing": 100},
    "favorite_colors": "GREEN",
    "favorite_language": "JS",
    "has_car": False,
    "country": "Argentina",
    "years_of_expirience": 5,
    "md5": "u00ff",
    "birthday": "2019-10-12",
    "meeting_time": "17:57:42",
    "release_datetime": "2019-10-12T17:57:42+0000",
    "event_uuid": "09f00184-7721-4266-a955-21048a5cc235",
}

advance_user_python_dict = {
    "name": "juan",
    "age": 20,
    "is_developer": True,
    "pets": ["dog", "cat"],
    "accounts": {"ing": 100},
    "has_car": False,
    "favorite_colors": FavoriteColor.GREEN,
    "favorite_language": FavoriteLanguage.JS,
    "country": "Argentina",
    "years_of_expirience": 5,
    "md5": b"u00ff",
    "birthday": datetime.date(2019, 10, 12),
    "meeting_time": datetime.time(17, 57, 42),
    "release_datetime": datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=UTC),
    "event_uuid": uuid.UUID("09f00184-7721-4266-a955-21048a5cc235"),
}

advance_user_avro_binary = b"\x08juan(\x01\x04\x06dog\x06cat\x00\x02\x06ing\xc8\x01\x00\x04\x04\x00\x12Argentina\n\nu00ff\x8a\x9c\x02\xe0\xa7\xd5=\xe0\xd7\xf3\x91\xb8[H09f00184-7721-4266-a955-21048a5cc235"  # noqa
advance_user_avro_json = b'{"name": "juan", "age": 20, "is_developer": true, "pets": ["dog", "cat"], "accounts": {"ing": 100}, "favorite_colors": "GREEN", "favorite_language": "JS", "has_car": false, "country": "Argentina", "years_of_expirience": 5, "md5": "u00ff", "birthday": 18181, "meeting_time": 64662000, "release_datetime": 1570903062000, "event_uuid": "09f00184-7721-4266-a955-21048a5cc235"}'  # noqa

CLASSES_DATA_BINARY = (
    (User, data_user, user_avro_binary, user_avro_json, user_json, user_json),
    (
        UserAdvance,
        advance_data,
        advance_user_avro_binary,
        advance_user_avro_json,
        advance_user_json,
        advance_user_python_dict,
    ),
)


@pytest.mark.parametrize(
    "klass, data, avro_binary, avro_json, instance_json, python_dict",
    CLASSES_DATA_BINARY,
)
def test_serialization(klass, data, avro_binary, avro_json, instance_json, python_dict):
    instance = klass(**data)

    assert instance.serialize() == avro_binary
    assert instance.serialize(serialization_type="avro-json") == avro_json


@pytest.mark.parametrize(
    "serialization_type, data",
    [(AVRO, b"\x02\x00\x00"), (AVRO_JSON, b'{"users": [{"color": "BLUE"}]}')],
)
def test_serialization_with_enum_in_sequences(serialization_type: SerializationType, data: bytes) -> None:
    @dataclass
    class UserModel(AvroModel):
        color: FavoriteColor = FavoriteColor.BLUE

    @dataclass
    class GroupModel(AvroModel):
        users: typing.List[UserModel]

    instance = GroupModel([UserModel()])
    assert instance.serialize(serialization_type=serialization_type) == data
    assert GroupModel.deserialize(data, serialization_type=serialization_type) == instance
    assert GroupModel.deserialize(data, serialization_type=serialization_type, create_instance=False) == {
        "users": [{"color": "BLUE"}]
    }


@pytest.mark.parametrize(
    "klass, data, avro_binary, avro_json, instance_json, python_dict",
    CLASSES_DATA_BINARY,
)
def test_deserialization(klass, data, avro_binary, avro_json, instance_json, python_dict):
    instance = klass(**data)

    assert instance.deserialize(avro_binary, create_instance=False) == python_dict
    assert instance.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == python_dict

    assert instance.deserialize(avro_binary) == instance
    assert instance.deserialize(avro_json, serialization_type="avro-json") == instance


@pytest.mark.parametrize(
    "klass, data, avro_binary, avro_json, instance_json, python_dict",
    CLASSES_DATA_BINARY,
)
def test_deserialization_with_class(klass, data, avro_binary, avro_json, instance_json, python_dict):
    instance = klass(**data)

    assert klass.deserialize(avro_binary, create_instance=False) == python_dict
    assert klass.deserialize(avro_json, serialization_type="avro-json", create_instance=False) == python_dict

    assert klass.deserialize(avro_binary) == instance
    assert klass.deserialize(avro_json, serialization_type="avro-json") == instance


def test_invalid_serialization_deserialization_types():
    user = User.parse_obj(data_user)

    with pytest.raises(ValueError):
        user.serialize(serialization_type="json")  # type: ignore

    with pytest.raises(ValueError):
        user.deserialize(b"", serialization_type="json")  # type: ignore


def test_deserialization_with_writer_schema_dict():
    user = User.parse_obj(data_user)
    writer_schema = User.avro_schema_to_python()
    UserCompatible.deserialize(user.serialize(), writer_schema=writer_schema)


def test_deserialization_with_writer_schema_avro_model():
    user = User.parse_obj(data_user)
    UserCompatible.deserialize(user.serialize(), writer_schema=User)
