import dataclasses
import datetime
import decimal
import typing
import uuid

from dataclasses_avroschema import AvroModel, types


def test_fake_primitive_types(user_dataclass: typing.Type[AvroModel]) -> None:
    assert isinstance(user_dataclass.fake(), user_dataclass)


def test_fake_complex_types(user_advance_dataclass: typing.Type[AvroModel]) -> None:
    assert isinstance(user_advance_dataclass.fake(), user_advance_dataclass)


def test_fake_with_user_data(user_advance_dataclass: typing.Type[AvroModel]) -> None:
    """
    Creates a fake with data provided by the end user

    user_advance_dataclass is the following type:

        @decorator
        class UserAdvance(AvroModel):
            name: str
            age: int
            pets: typing.List[str]
            accounts: typing.Dict[str, int]
            favorite_colors: color_enum
            has_car: bool = False
            country: str = "Argentina"
            address: typing.Optional[str] = None
            md5: types.Fixed = types.Fixed(16)
    """
    name = "bond"
    age = 10
    pets = ["dog", "cat"]

    user_advance = user_advance_dataclass.fake(name=name, age=age, pets=pets)
    assert isinstance(user_advance, user_advance_dataclass)

    # check that the data provided with the end user was used by the fake
    assert user_advance.name == name
    assert user_advance.age == 10
    assert user_advance.pets == pets


def test_fake_with_logical_types() -> None:
    @dataclasses.dataclass
    class LogicalTypes(AvroModel):
        birthday: datetime.date
        meeting_time: datetime.time
        meeting_time_micro: types.TimeMicro
        release_datetime: datetime.datetime
        release_datetime_micro: types.DateTimeMicro
        time_elapsed: datetime.timedelta
        event_uuid: uuid.UUID

    assert isinstance(LogicalTypes.fake(), LogicalTypes)


def test_fake_union() -> None:
    @dataclasses.dataclass
    class Bus(AvroModel):
        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    @dataclasses.dataclass
    class Car(AvroModel):
        engine_name: str

        class Meta:
            namespace = "types.car_type"

    @dataclasses.dataclass
    class UnionSchema(AvroModel):
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.UUID]
        lake_trip: typing.Union[Bus, Car]
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: Bus(engine_name="honda"))
        river_trip: typing.Optional[typing.Union[Bus, Car]] = None

    assert isinstance(UnionSchema.fake(), UnionSchema)


def test_fake_one_to_one_relationship() -> None:
    """
    Test schema relationship one-to-one
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        address: Address

    assert isinstance(User.fake(), User)


def test_fake_one_to_many_relationship() -> None:
    """
    Test schema relationship one-to-many
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        addresses: typing.List[Address]

    user = User.fake()
    assert isinstance(user, User)
    assert User.avro_schema()


def test_fake_one_to_many_with_tuples() -> None:
    """
    Test schema relationship one-to-many
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        addresses: typing.Tuple[Address, ...]

    user = User.fake()
    assert isinstance(user, User)
    assert User.avro_schema()
    assert isinstance(user.addresses, tuple)


def test_fake_one_to_many_map_relationship() -> None:
    """
    Test schema relationship one-to-many using a map
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    assert isinstance(User.fake(), User)


def test_self_one_to_one_relationship() -> None:
    """
    Test self relationship one-to-one
    """

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        teamates: typing.Optional[typing.Type["User"]] = None

    assert isinstance(User.fake(), User)


# TODO: add pydantic test
def test_self_one_to_many_relationship() -> None:
    """
    Test self relationship one-to-many
    """

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        points: typing.List[typing.Optional[types.Float32]]
        teamates: typing.Optional[typing.List[typing.Type["User"]]] = None

    assert isinstance(User.fake(), User)


# TODO: add pydantic test
def test_self_one_to_many_map_relationship() -> None:
    """
    Test self relationship one-to-many Map
    """

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]]
        teamates: typing.Optional[typing.Dict[str, typing.Type["User"]]] = None

    assert isinstance(User.fake(), User)


def test_optional_relationship() -> None:
    @dataclasses.dataclass
    class Address(AvroModel):
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        address: typing.Optional[Address] = None

    assert isinstance(User.fake(), User)


def test_decimals() -> None:
    """
    Test Decimal logical types
    """

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        test_score_1: types.condecimal(max_digits=11, decimal_places=5)
        test_score_2: types.condecimal(max_digits=5, decimal_places=2) = decimal.Decimal("100.00")

    assert isinstance(User.fake(), User)


def test_int32() -> None:
    """
    Test Int32 type
    """

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        test_score_1: types.Int32 = 100
        test_score_2: types.Int32 = types.Int32(12)

    assert isinstance(User.fake(), User)


def test_float32() -> None:
    """
    Test Float32 type
    """

    @dataclasses.dataclass
    class User(AvroModel):
        name: str
        age: int
        test_score_1: types.Float32 = 100.0
        test_score_2: types.Float32 = types.Float32(12.4)

    assert isinstance(User.fake(), User)
