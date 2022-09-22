import dataclasses
import datetime
import typing
import uuid

from fastavro import parse_schema

from dataclasses_avroschema import AvroModel, DateTimeMicro, TimeMicro, field_utils


def test_minimal_schema(user_dataclass):
    """
    Python class contains the primitive types:

    class User:
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes
    """
    schema = user_dataclass.avro_schema_to_python()

    assert parse_schema(schema)


def test_schema_with_field_metadata(user_dataclass_with_field_metadata):
    """
    Python class contains the primitive types:

    class User:
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes
    """
    schema = user_dataclass_with_field_metadata.avro_schema_to_python()

    assert parse_schema(schema)


def test_schema_with_extra_avro_attrs(user_extra_avro_atributes_dataclass):
    """
    Python class contains the primitive types plus aliases and namespace

    class UserAliasesNamespace:
        name: str
        age: int

        def extra_avro_attributes() -> typing.Dict[str, typing.Any]:
            return {
                "namespace": "test.com.ar/user/v1",
                "aliases": ["User", "My favorite User"]
            }
    """
    schema = user_extra_avro_atributes_dataclass.avro_schema_to_python()
    assert parse_schema(schema)


def test_advance_schema(user_advance_dataclass, user_advance_dataclass_with_union_enum):
    """
    Python class contains the primitive, primitive with default values
    array, enum, map types.

    class FavoriteColor(enum.Enum):
        BLUE = "BLUE"
        YELLOW = "YELLOW"
        GREEN = "GREEN"

    class UserAdvance:
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: FavoriteColor
        has_car: bool = False
        country: str = "Argentina"
        address: str = None
        md5: types.Fixed = types.Fixed(16)
    """
    schema = user_advance_dataclass.avro_schema_to_python()
    assert parse_schema(schema)

    schema = user_advance_dataclass_with_union_enum.avro_schema_to_python()
    assert parse_schema(schema)


def test_advance_schema_with_defaults(user_advance_with_defaults_dataclass):
    """
    Python class contains the primitive, primitive with default values
    array, enum, map types.

    class FavoriteColor(enum.Enum):
        BLUE = "BLUE"
        YELLOW = "YELLOW"
        GREEN = "GREEN"

    class UserAdvance:
        name: str
        age: int
        pets: typing.List[str] = dataclasses.field(default_factory=lambda: ['dog', 'cat'])
        accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: FavoriteColor = FavoriteColor.BLUE
        country: str = "Argentina"
        address: str = None
    """
    schema = user_advance_with_defaults_dataclass.avro_schema_to_python()
    assert parse_schema(schema)


def test_one_to_one_schema():
    """
    Test relationship one-to-one
    """

    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "An User with Address"
        name: str
        age: int
        address: Address

    assert parse_schema(User.avro_schema_to_python())


def test_one_to_one_repeated_schema():
    """
    Test relationship one-to-one with more than once schema
    """

    class Location(AvroModel):
        latitude: float
        longitude: float

        class Meta:
            namespace = "types.location_type"

    class Trip(AvroModel):
        start_time: datetime.datetime
        start_location: Location
        finish_time: datetime.datetime
        middle_location: Location
        finish_location: typing.List[Location]

    assert parse_schema(Trip.avro_schema_to_python())
    assert Trip.fake()


def test_one_to_one_repeated_schema_in_array():
    """
    Test relationship one-to-one with more than once schema
    """

    class Location(AvroModel):
        latitude: float
        longitude: float

        class Meta:
            namespace = "types.location_type"

    class Trip(AvroModel):
        start_time: datetime.datetime
        start_location: Location
        finish_time: datetime.datetime
        finish_location: typing.List[Location]

    assert parse_schema(Trip.avro_schema_to_python())
    assert Trip.fake()


def test_one_to_one_repeated_schema_in_map():
    """
    Test relationship one-to-one with more than once schema
    """

    class Location(AvroModel):
        latitude: float
        longitude: float

        class Meta:
            namespace = "types.location_type"

    class Trip(AvroModel):
        start_time: datetime.datetime
        start_location: Location
        finish_time: datetime.datetime
        finish_location: typing.Dict[str, Location]

    assert parse_schema(Trip.avro_schema_to_python())
    assert Trip.fake()


def test_one_to_many_repeated_schema_in_array_and_map():
    class User(AvroModel):
        name: str

        class Meta:
            schema_doc = False
            namespace = "types.user"

    class UserAdvance(AvroModel):
        users: typing.List[User]
        accounts: typing.Dict[str, User]

        class Meta:
            schema_doc = False

    assert parse_schema(UserAdvance.avro_schema_to_python())
    assert UserAdvance.fake()


def test_one_to_many_schema():
    """
    Test relationship one-to-many
    """

    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    assert parse_schema(User.avro_schema_to_python())


def test_one_to_many_with_map_schema():
    """
    Test relationship one-to-many using a map
    """

    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    assert parse_schema(User.avro_schema_to_python())


def test_one_to_one_self_relationship():
    """
    Test self relationship one-to-one
    """

    class User(AvroModel):
        "User with self reference as friend"
        name: str
        age: int
        friend: typing.Type["User"]

    assert parse_schema(User.avro_schema_to_python())


def test_one_to_many_self_reference_schema():
    """
    Test self relationship one-to-many using an array
    """

    class User(AvroModel):
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.List[typing.Type["User"]]

    assert parse_schema(User.avro_schema_to_python())


def test_one_to_many_self_reference_map_schema():
    """
    Test self relationship one-to-many using a map
    """

    class User(AvroModel):
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]]

    assert parse_schema(User.avro_schema_to_python())


def test_logical_types_schema():
    """
    Test a schema with Logical Types
    """
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, 179133)

    class LogicalTypes(AvroModel):
        "Some logical types"
        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"

    assert parse_schema(LogicalTypes.avro_schema_to_python())


def test_logical_micro_types_schema():
    """
    Test a schema with Logical Types with Micros
    """
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)

    class LogicalTypesMicro(AvroModel):
        "Some logical types"
        time_micros: TimeMicro
        datetime_micros: DateTimeMicro
        meeting_time: datetime.time = a_datetime.time()
        meeting_datetime: datetime.datetime = a_datetime
        meeting_time_micros: TimeMicro = a_datetime.time()
        meeting_datetime_micros: DateTimeMicro = a_datetime
        release_datetime: datetime.datetime = a_datetime

    assert parse_schema(LogicalTypesMicro.avro_schema_to_python())


def test_schema_with_union_types():
    class UnionSchema(AvroModel):
        "Some Unions"
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        optional_union: typing.Optional[str]
        optional_union_with_default: typing.Optional[str] = None
        second_union: typing.Union[str, int] = dataclasses.field(default_factory=lambda: ["test"])

    assert parse_schema(UnionSchema.avro_schema_to_python())


def test_schema_with_union_record_types():
    class Bus(AvroModel):
        "A Bus"
        engine_name: str

    class Car(AvroModel):
        "A Car"
        engine_name: str

    class UnionSchema(AvroModel):
        "Some Unions"
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: {"engine_name": "honda"})

    assert parse_schema(UnionSchema.avro_schema_to_python())


def test_schema_array_with_union_types():
    class ArrayUnionSchema(AvroModel):
        "Array Some Unions"
        first_union: typing.List[typing.Union[str, int]]
        second_union: typing.List[typing.Union[str, int]] = dataclasses.field(default_factory=lambda: ["test"])

    assert parse_schema(ArrayUnionSchema.avro_schema_to_python())


def test_namespaces():
    class C(AvroModel):
        pass

    class B(AvroModel):
        c: C

        class Meta:
            namespace = "my.namespace"

    class A(AvroModel):
        b1: B
        b2: B

    parse_schema(A.avro_schema_to_python())


def test_use_of_same_type_in_nested_list():
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

        class Meta:
            namespace = "types.test"

    class PreviousAddresses(AvroModel):
        addresses: typing.List[Address]

    class User(AvroModel):
        "An User with Address and previous addresses"
        name: str
        age: int
        address: Address
        previous_addresses: PreviousAddresses

    assert parse_schema(User.avro_schema_to_python())


def test_two_different_child_records():
    class Location(AvroModel):
        lat: float
        long: float
        altitude: typing.Optional[float] = None
        bearing: typing.Optional[float] = None

        class Meta:
            namespace = "test.namespace"

    class Photo(AvroModel):
        filename: str
        data: bytes
        width: int
        height: int
        geo_tag: typing.Optional[Location] = None

    class Video(AvroModel):
        filename: str
        data: bytes
        duration: int
        geo_tag: typing.Optional[Location] = None

    class HolidayAlbum(AvroModel):
        album_name: str
        photos: typing.List[Photo] = dataclasses.field(default_factory=list)
        videos: typing.List[Video] = dataclasses.field(default_factory=list)

        class Meta:
            namespace = "test.namespace"

    assert parse_schema(HolidayAlbum.avro_schema_to_python())
