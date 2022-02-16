import dataclasses
import enum
import typing

import pytest

from dataclasses_avroschema import AvroModel, types


@pytest.fixture
def color_enum():
    class FavoriteColor(enum.Enum):
        BLUE = "BLUE"
        YELLOW = "YELLOW"
        GREEN = "GREEN"

    return FavoriteColor


@pytest.fixture
def user_type_enum():
    class UserType(enum.Enum):
        BASIC = "BASIC"
        PREMIUM = "PREMIUM"

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
def user_advance_dataclass(color_enum):
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: color_enum
        has_car: bool = False
        country: str = "Argentina"
        address: str = None
        md5: types.Fixed = types.Fixed(16)

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_dataclass_with_enum(color_enum: type, user_type_enum: type):
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: color_enum
        has_car: bool = False
        country: str = "Argentina"
        address: str = None
        user_type: typing.Optional[user_type_enum] = None
        md5: types.Fixed = types.Fixed(16)

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_dataclass_with_union_enum(color_enum: type, user_type_enum: type):
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: color_enum
        has_car: bool = False
        country: str = "Argentina"
        address: str = None
        user_type: typing.Union[int, user_type_enum] = -1
        md5: types.Fixed = types.Fixed(16)

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_dataclass_with_sub_record_and_enum(color_enum: type, user_type_enum: type):
    @dataclasses.dataclass
    class SubRecord(AvroModel):
        sub_name: str
        user_type: typing.Union[int, user_type_enum]

    @dataclasses.dataclass
    class UserWithSubRecordAndEnum(AvroModel):
        name: str
        favorite_colors: color_enum
        sub_record: SubRecord
        has_car: bool = False

        class Meta:
            schema_doc = False

    return UserWithSubRecordAndEnum


@pytest.fixture
def user_advance_with_defaults_dataclass(color_enum):
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str] = dataclasses.field(default_factory=lambda: ["dog", "cat"])
        accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: color_enum = color_enum.BLUE
        country: str = "Argentina"
        address: str = None

        class Meta:
            schema_doc = False

    return UserAdvance


@pytest.fixture
def user_advance_with_defaults_dataclass_with_enum(color_enum, user_type_enum):
    @dataclasses.dataclass
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str] = dataclasses.field(default_factory=lambda: ["dog", "cat"])
        accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: color_enum = color_enum.BLUE
        country: str = "Argentina"
        address: str = None
        user_type: typing.Optional[user_type_enum] = None

        class Meta:
            schema_doc = False

    return UserAdvance
