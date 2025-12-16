import dataclasses
import enum
import logging
import typing

import pytest
from typing_extensions import Annotated

from dataclasses_avroschema import AvroModel, types

# set the faker loglevel to info to avoid noise during testing
logging.getLogger("faker").setLevel(logging.INFO)


class FavoriteColor(str, enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class UserType(str, enum.Enum):
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"


@pytest.fixture
def color_enum():
    return FavoriteColor


@pytest.fixture
def user_type_enum():
    return UserType


@pytest.fixture
def user_dataclass():
    @dataclasses.dataclass(repr=False)
    class User(AvroModel):
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

        class Meta:
            schema_doc = False

    return User


@pytest.fixture
def user_dataclass_with_doc():
    @dataclasses.dataclass(repr=False)
    class User(AvroModel):
        """I am documented."""

        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

    return User


@pytest.fixture
def user_dataclass_with_field_metadata():
    @dataclasses.dataclass(repr=False)
    class User(AvroModel):
        name: str = dataclasses.field(metadata={"classification": "test"})
        age: int = dataclasses.field(metadata={"classification": "test"})
        has_pets: bool = dataclasses.field(metadata={"classification": "test"})
        money: float = dataclasses.field(metadata={"classification": "test"})
        encoded: bytes = dataclasses.field(metadata={"classification": "test"})

        class Meta:
            schema_doc = False

    return User


@pytest.fixture
def user_v2_dataclass():
    @dataclasses.dataclass(repr=False)
    class UserV2(AvroModel):
        "A User V2"

        name: str
        age: int

    return UserV2


@pytest.fixture
def user_extra_avro_atributes_dataclass():
    @dataclasses.dataclass(repr=False)
    class UserAliasesNamespace(AvroModel):
        name: str
        age: int

        def extra_avro_attributes() -> typing.Dict[str, typing.Any]:
            return {
                "namespace": "test.com.ar/user/v1",
                "aliases": ["User", "My favorite User"],
            }

    return UserAliasesNamespace


@pytest.fixture
def user_advance_dataclass():
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: FavoriteColor
        md5: types.confixed(size=16)
        has_car: bool = False
        country: str = "Argentina"
        address: typing.Optional[str] = None

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_dataclass_with_enum():
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: FavoriteColor
        md5: types.confixed(size=16)
        has_car: bool = False
        country: str = "Argentina"
        address: typing.Optional[str] = None
        user_type: typing.Optional[UserType] = None

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_dataclass_with_union_enum():
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: FavoriteColor
        md5: types.confixed(size=16)
        has_car: bool = False
        country: str = "Argentina"
        address: typing.Optional[str] = None
        user_type: typing.Union[int, UserType] = -1

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_dataclass_with_union_enum_with_annotated():
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: Annotated[str, "string"]
        age: Annotated[int, "integer"]
        pets: typing.List[Annotated[str, "string"]]
        accounts: typing.Dict[str, Annotated[int, "integer"]]
        favorite_colors: Annotated[FavoriteColor, "a color enum"]
        md5: types.confixed(size=16)
        has_car: Annotated[bool, "boolean"] = False
        country: str = "Argentina"
        address: typing.Optional[Annotated[str, "string"]] = None
        user_type: typing.Union[Annotated[int, "integer"], UserType] = -1

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_dataclass_with_sub_record_and_enum():
    @dataclasses.dataclass
    class SubRecord(AvroModel):
        sub_name: str
        user_type: typing.Union[int, UserType]

    @dataclasses.dataclass
    class UserWithSubRecordAndEnum(AvroModel):
        name: str
        favorite_colors: FavoriteColor
        sub_record: SubRecord
        has_car: bool = False

        class Meta:
            schema_doc = False

    return UserWithSubRecordAndEnum


@pytest.fixture
def user_advance_with_defaults_dataclass():
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str] = dataclasses.field(default_factory=lambda: ["dog", "cat"])
        accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: FavoriteColor = FavoriteColor.BLUE
        country: str = "Argentina"
        address: typing.Optional[str] = None

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_with_defaults_dataclass_with_enum():
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str] = dataclasses.field(default_factory=lambda: ["dog", "cat"])
        accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: FavoriteColor = FavoriteColor.BLUE
        country: str = "Argentina"
        address: typing.Optional[str] = None
        user_type: typing.Optional[UserType] = None

        class Meta:
            schema_doc = False

    return UserAdvance
