import os

import json

import dataclasses

import typing

import pytest


SCHEMA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "schemas"
)

AVRO_SCHEMAS_DIR = os.path.join(SCHEMA_DIR, "avro")
JSON_SCHEMAS_DIR = os.path.join(SCHEMA_DIR, "json")


def load(fp):
    with open(fp, mode="r") as f:
        return f.read()


@pytest.fixture
def user_dataclass():
    @dataclasses.dataclass(repr=False)
    class User:
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

    return User


@pytest.fixture
def user_v2_dataclass():
    @dataclasses.dataclass(repr=False)
    class UserV2:
        "A User V2"
        name: str
        age: int

    return UserV2


@pytest.fixture
def user_extra_avro_atributes_dataclass():
    @dataclasses.dataclass(repr=False)
    class UserAliasesNamespace:
        name: str
        age: int

        def extra_avro_attributes() -> typing.Dict[str, typing.Any]:
            return {
                "namespace": "test.com.ar/user/v1",
                "aliases": ["User", "My favorite User"]
            }

    return UserAliasesNamespace


@pytest.fixture
def user_advance_dataclass():
    class UserAdvance:
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        has_car: bool = False
        favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
        country: str = "Argentina"
        address: str = None

    return UserAdvance


@pytest.fixture
def user_avro_json():
    user_avro_path = os.path.join(AVRO_SCHEMAS_DIR, "user.avsc")
    schema_string = load(user_avro_path)
    return json.loads(schema_string)


@pytest.fixture
def user_v2_avro_json():
    user_avro_path = os.path.join(AVRO_SCHEMAS_DIR, "user_v2.avsc")
    schema_string = load(user_avro_path)
    return json.loads(schema_string)


@pytest.fixture
def user_advance_avro_json():
    user_avro_path = os.path.join(AVRO_SCHEMAS_DIR, "user_advance.avsc")
    schema_string = load(user_avro_path)
    return json.loads(schema_string)


@pytest.fixture
def user_extra_avro_attributes():
    user_avro_path = os.path.join(AVRO_SCHEMAS_DIR, "user_extra_avro_attributes.avsc")
    schema_string = load(user_avro_path)
    return json.loads(schema_string)


@pytest.fixture
def user_one_address_schema():
    user_avro_path = os.path.join(AVRO_SCHEMAS_DIR, "user_one_address.avsc")
    schema_string = load(user_avro_path)
    return json.loads(schema_string)

