import dataclasses
import datetime
import typing
import uuid

from fastavro import parse_schema

from dataclasses_avroschema import AvroModel, DateTimeMicro, TimeMicro


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

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"

        street: str
        street_number: int

    @dataclasses.dataclass
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

    @dataclasses.dataclass
    class Location(AvroModel):
        latitude: float
        longitude: float

        class Meta:
            namespace = "types.location_type"

    @dataclasses.dataclass
    class Trip(AvroModel):
        start_time: datetime.datetime
        start_location: Location
        finish_time: datetime.datetime
        middle_location: Location
        finish_location: typing.List[Location]

    assert parse_schema(Trip.avro_schema_to_python())
    assert Trip.fake()


def test_repeated_schema_without_namespace():
    @dataclasses.dataclass
    class Bus(AvroModel):
        "A Bus"

        engine_name: str

    @dataclasses.dataclass
    class UnionSchema(AvroModel):
        "Some Unions"

        bus_one: Bus
        bus_two: Bus

    parse_schema(UnionSchema.avro_schema_to_python())


def test_one_to_one_repeated_schema_in_array():
    """
    Test relationship one-to-one with more than once schema
    """

    @dataclasses.dataclass
    class Location(AvroModel):
        latitude: float
        longitude: float

        class Meta:
            namespace = "types.location_type"

    @dataclasses.dataclass
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

    @dataclasses.dataclass
    class Location(AvroModel):
        latitude: float
        longitude: float

        class Meta:
            namespace = "types.location_type"

    @dataclasses.dataclass
    class Trip(AvroModel):
        start_time: datetime.datetime
        start_location: Location
        finish_time: datetime.datetime
        finish_location: typing.Dict[str, Location]

    assert parse_schema(Trip.avro_schema_to_python())
    assert Trip.fake()


def test_one_to_many_repeated_schema_in_array_and_map():
    @dataclasses.dataclass
    class User(AvroModel):
        name: str

        class Meta:
            schema_doc = False
            namespace = "types.user"

    @dataclasses.dataclass
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

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"

        street: str
        street_number: int

    @dataclasses.dataclass
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

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"

        street: str
        street_number: int

    @dataclasses.dataclass
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

    @dataclasses.dataclass
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

    @dataclasses.dataclass
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

    @dataclasses.dataclass
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

    @dataclasses.dataclass
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

    @dataclasses.dataclass
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
    @dataclasses.dataclass
    class UnionSchema(AvroModel):
        "Some Unions"

        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        optional_union: typing.Optional[str]
        optional_union_with_default: typing.Optional[str] = None
        second_union: typing.Union[str, int] = "test"

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

        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: Bus(engine_name="honda"))

    assert parse_schema(UnionSchema.avro_schema_to_python())


def test_schema_array_with_union_types():
    class ArrayUnionSchema(AvroModel):
        "Array Some Unions"

        first_union: typing.List[typing.Union[str, int]]
        second_union: typing.List[typing.Union[str, int]] = dataclasses.field(default_factory=lambda: ["test"])

    assert parse_schema(ArrayUnionSchema.avro_schema_to_python())


def test_schema_fullname():
    class B(AvroModel):
        ...

        class Meta:
            namespace = "my.namespace"

    class A(AvroModel): ...

    assert A.get_fullname() == "A"
    assert B.get_fullname() == "my.namespace.B"

    # check that A is inside the `__named_schemas`
    parsed_schema = parse_schema(A.avro_schema_to_python())
    assert A.get_fullname() in parsed_schema["__named_schemas"].keys()

    # check that B is inside the `__named_schemas`
    parsed_schema = parse_schema(B.avro_schema_to_python())
    assert B.get_fullname() in parsed_schema["__named_schemas"].keys()


def test_schema_fullname_nested_records():
    @dataclasses.dataclass
    class C(AvroModel):
        name: str
        age: int

    @dataclasses.dataclass
    class B(AvroModel):
        c: C

        class Meta:
            namespace = "my.namespace"

    @dataclasses.dataclass
    class A(AvroModel):
        b1: B
        b2: B

    assert A.get_fullname() == "A"
    assert B.get_fullname() == "my.namespace.B"
    assert C.get_fullname() == "C"

    # check that A is inside the `__named_schemas`
    parsed_schema = parse_schema(A.avro_schema_to_python())
    assert A.get_fullname() in parsed_schema["__named_schemas"].keys()

    # check that B is inside the `__named_schemas`
    parsed_schema = parse_schema(B.avro_schema_to_python())
    assert B.get_fullname() in parsed_schema["__named_schemas"].keys()

    # check that C is inside the `__named_schemas`
    # parsed_schema = parse_schema(C.avro_schema_to_python())
    assert C.get_fullname() in parsed_schema["__named_schemas"].keys()


def test_use_of_same_type_in_nested_list():
    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"

        street: str
        street_number: int

        class Meta:
            namespace = "types.test"

    @dataclasses.dataclass
    class PreviousAddresses(AvroModel):
        addresses: typing.List[Address]

    @dataclasses.dataclass
    class User(AvroModel):
        "An User with Address and previous addresses"

        name: str
        age: int
        address: Address
        previous_addresses: PreviousAddresses

    assert parse_schema(User.avro_schema_to_python())


def test_two_different_child_records():
    @dataclasses.dataclass
    class Location(AvroModel):
        lat: float
        long: float
        altitude: typing.Optional[float] = None
        bearing: typing.Optional[float] = None

        class Meta:
            namespace = "test.namespace"

    @dataclasses.dataclass
    class Photo(AvroModel):
        filename: str
        data: bytes
        width: int
        height: int
        geo_tag: typing.Optional[Location] = None

    @dataclasses.dataclass
    class Video(AvroModel):
        filename: str
        data: bytes
        duration: int
        geo_tag: typing.Optional[Location] = None

    @dataclasses.dataclass
    class HolidayAlbum(AvroModel):
        album_name: str
        photos: typing.List[Photo] = dataclasses.field(default_factory=list)
        videos: typing.List[Video] = dataclasses.field(default_factory=list)

        class Meta:
            namespace = "test.namespace"

    assert parse_schema(HolidayAlbum.avro_schema_to_python())


def test_nested_schemas_splitted() -> None:
    """
    This test will cover the cases when nested schemas are
    used in a separate way.
    """

    @dataclasses.dataclass
    class A(AvroModel):
        class Meta:
            namespace = "namespace"

    @dataclasses.dataclass
    class B(AvroModel):
        a: A

    @dataclasses.dataclass
    class C(AvroModel):
        b: B
        a: A

    # first the B schema is generated
    assert parse_schema(B.avro_schema_to_python())

    # then check that the C schema is valid
    assert parse_schema(C.avro_schema_to_python())


def test_nested_scheamas_splitted_with_intermediates() -> None:
    @dataclasses.dataclass
    class A(AvroModel):
        class Meta:
            namespace = "namespace"

    class B(AvroModel):
        a: A

    @dataclasses.dataclass
    class C(AvroModel):
        a: A

    @dataclasses.dataclass
    class D(AvroModel):
        b: B
        c: C

    # first the B schema is generated
    assert parse_schema(D.avro_schema_to_python())

    # then check that the C schema is valid
    assert parse_schema(C.avro_schema_to_python())
