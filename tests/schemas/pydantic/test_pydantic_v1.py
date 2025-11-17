import datetime
import decimal
import enum
import json
import typing
import uuid

import pytest
from pydantic.v1 import (
    UUID1,
    AmqpDsn,
    CockroachDsn,
    EmailStr,
    Field,
    KafkaDsn,
    MongoDsn,
    PositiveInt,
    PostgresDsn,
    RedisDsn,
    ValidationError,
)

from dataclasses_avroschema import types, utils
from dataclasses_avroschema.pydantic.v1 import AvroBaseModel

if utils.is_python_314_or_newer():
    pytest.skip(
        allow_module_level=True, reason="Pydantic v1 is not supported in Python 3.14 or newer"
    )  # pragma: no cover

encoded = "test".encode()


def test_pydantic_record_schema_primitive_types(user_avro_json):
    class User(AvroBaseModel):
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

        class Meta:
            schema_doc = False

    assert User.avro_schema() == json.dumps(user_avro_json)


def test_exclude_default_from_schema(user_avro_json):
    class User(AvroBaseModel):
        name: str = Field(default="marcos", metadata={"exclude_default": True})
        age: int = Field(default=20, metadata={"exclude_default": True})
        has_pets: bool = Field(default=True, metadata={"exclude_default": True})
        money: float = Field(default=100.5, metadata={"exclude_default": True})
        encoded: bytes = Field(default=b"batman", metadata={"exclude_default": True})

        class Meta:
            schema_doc = False

    assert User.avro_schema() == json.dumps(user_avro_json)


def test_pydantic_record_schema_with_metadata():
    class User(AvroBaseModel):
        name: str = Field(metadata={"doc": "bar"})

        class Meta:
            schema_doc = False

    expected_schema = {
        "type": "record",
        "name": "User",
        "fields": [{"doc": "bar", "name": "name", "type": "string"}],
    }
    assert User.avro_schema() == json.dumps(expected_schema)


def test_pydantic_record_schema_complex_types(user_advance_avro_json, color_enum):
    class UserAdvance(AvroBaseModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: color_enum
        md5: types.confixed(size=16)
        has_car: bool = False
        country: str = "Argentina"
        address: typing.Optional[str] = None

        class Meta:
            schema_doc = False

        class Config:
            arbitrary_types_allowed = True

    assert UserAdvance.avro_schema() == json.dumps(user_advance_avro_json)


def test_pydantic_record_schema_complex_types_with_defaults(user_advance_with_defaults_avro_json, color_enum):
    class UserAdvance(AvroBaseModel):
        name: str
        age: int
        pets: typing.List[str] = Field(default_factory=lambda: ["dog", "cat"])
        accounts: typing.Dict[str, int] = Field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: color_enum = color_enum.BLUE
        country: str = "Argentina"
        address: str = None

        class Meta:
            schema_doc = False

    assert UserAdvance.avro_schema() == json.dumps(user_advance_with_defaults_avro_json)


def test_pydantic_record_schema_logical_types(logical_types_schema):
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)
    delta = datetime.timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5, milliseconds=6, microseconds=7)

    class LogicalTypes(AvroBaseModel):
        "Some logical types"

        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        time_elapsed: datetime.timedelta = delta
        event_uuid: uuid.UUID = "09f00184-7721-4266-a955-21048a5cc235"

    assert LogicalTypes.avro_schema() == json.dumps(logical_types_schema)


def test_pydantic_record_one_to_one_relationship(user_one_address_schema):
    """
    Test schema relationship one-to-one
    """

    class Address(AvroBaseModel):
        "An Address"

        street: str
        street_number: int

    class User(AvroBaseModel):
        "An User with Address"

        name: str
        age: int
        address: Address

    assert User.avro_schema() == json.dumps(user_one_address_schema)


def test_pydantic_record_one_to_one_relationship_with_none_default(
    user_one_address_schema_with_none_default,
):
    """
    Test schema relationship one-to-one
    """

    class Address(AvroBaseModel):
        "An Address"

        street: str
        street_number: int

    class User(AvroBaseModel):
        "An User with Address"

        name: str
        age: int
        address: Address = None

    assert User.avro_schema() == json.dumps(user_one_address_schema_with_none_default)


def test_pydantic_record_one_to_many_relationship(user_many_address_schema):
    """
    Test schema relationship one-to-many
    """

    class Address(AvroBaseModel):
        "An Address"

        street: str
        street_number: int

    class User(AvroBaseModel):
        "User with multiple Address"

        name: str
        age: int
        addresses: typing.List[Address]

    assert User.avro_schema() == json.dumps(user_many_address_schema)


def test_pydantic_record_one_to_many_map_relationship(user_many_address_map_schema):
    """
    Test schema relationship one-to-many using a map
    """

    class Address(AvroBaseModel):
        "An Address"

        street: str
        street_number: int

    class User(AvroBaseModel):
        "User with multiple Address"

        name: str
        age: int
        addresses: typing.Dict[str, Address]

    assert User.avro_schema() == json.dumps(user_many_address_map_schema)


def test_pydantic_record_self_one_to_one_relationship(
    user_self_reference_one_to_one_schema,
):
    """
    Test self relationship one-to-one
    """

    class User(AvroBaseModel):
        "User with self reference as friend"

        name: str
        age: int
        friend: typing.Type["User"]
        teamates: typing.Type["User"] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_one_schema)


def test_pydantic_record_self_one_to_many_relationship(
    user_self_reference_one_to_many_schema,
):
    """
    Test self relationship one-to-many
    """

    class User(AvroBaseModel):
        "User with self reference as friends"

        name: str
        age: int
        friends: typing.List[typing.Type["User"]]
        teamates: typing.List[typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_many_schema)


def test_pydantic_record_self_one_to_many_map_relationship(
    user_self_reference_one_to_many_map_schema,
):
    """
    Test self relationship one-to-many Map
    """

    class User(AvroBaseModel):
        "User with self reference as friends"

        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]]
        teamates: typing.Dict[str, typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_many_map_schema)


def test_pydantic_record_schema_with_unions_type(union_type_schema):
    class Bus(AvroBaseModel):
        "A Bus"

        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    class Car(AvroBaseModel):
        "A Car"

        engine_name: str

        class Meta:
            namespace = "types.car_type"

    class TripDistance(enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"
            namespace = "trip"

    class UnionSchema(AvroBaseModel):
        "Some Unions"

        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, datetime.timedelta, uuid.UUID]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Union[Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = Field(default_factory=lambda: Bus(engine_name="honda"))
        trip_distance: typing.Union[int, TripDistance] = None
        optional_distance: typing.Optional[TripDistance] = None

    assert UnionSchema.avro_schema() == json.dumps(union_type_schema)


def test_pydantic_fields(pydantic_fields_schema):
    class Infrastructure(AvroBaseModel):
        email: EmailStr
        postgres_dsn: PostgresDsn
        cockroach_dsn: CockroachDsn
        amqp_dsn: AmqpDsn
        redis_dsn: RedisDsn
        mongo_dsn: MongoDsn
        kafka_url: KafkaDsn
        total_nodes: PositiveInt
        event_id: UUID1
        landing_zone_nodes: typing.List[PositiveInt]
        total_nodes_in_aws: PositiveInt = 10
        optional_kafka_url: typing.Optional[KafkaDsn] = None

    assert Infrastructure.avro_schema() == json.dumps(pydantic_fields_schema)


def test_create_instance():
    class User(AvroBaseModel):
        name: str
        age: int
        has_pets: bool = True

    User(
        name="a name",
        age=20,
    )

    with pytest.raises(ValueError):
        User()


def test_validate():
    class User(AvroBaseModel):
        name: str
        age: int
        has_pets: bool = True

    with pytest.raises(ValidationError):
        User.validate({"name": "a name"})

    user = User.validate(
        {
            "name": "a name",
            "age": 20,
        }
    )

    assert user.validate_avro()


def test_json_schema(AvroBaseModelV1):
    assert AvroBaseModelV1.json_schema()


def test_to_dict(AvroBaseModelV1):
    instance = AvroBaseModelV1(first_union="hi!", logical_union=uuid.uuid4())
    assert instance.to_dict() == instance.dict()


def test_asdict():
    class MyEnum(str, enum.Enum):
        x = "test"

    class ModelA(AvroBaseModel):
        a: int = 1
        d: MyEnum = MyEnum.x

    class ModelB(AvroBaseModel):
        b: ModelA
        d: MyEnum = MyEnum.x

    target = repr({"b": {"a": 1, "d": "test"}, "d": "test"})
    model_b = ModelB(b=ModelA())
    res_asdict = repr(model_b.asdict())
    assert res_asdict == target, res_asdict
    assert model_b.serialize()


def test_to_json(AvroBaseModelV1):
    instance = AvroBaseModelV1(first_union="hi!", logical_union=uuid.uuid4())
    assert instance.to_json() == instance.json()


def test_to_json_logical_types():
    class LogicalTypes(AvroBaseModel):
        "Some logical types"

        birthday: datetime.date
        meeting_time: datetime.time
        release_datetime: datetime.datetime
        event_uuid: uuid.UUID

    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)

    data = {
        "birthday": a_datetime.date(),
        "meeting_time": a_datetime.time(),
        "release_datetime": a_datetime,
        "event_uuid": uuid.UUID("09f00184-7721-4266-a955-21048a5cc235"),
    }

    logical_types = LogicalTypes(**data)
    avro_json = logical_types.serialize(serialization_type="avro-json")
    to_json = logical_types.json()

    assert logical_types.to_json() == to_json
    assert to_json.encode() != avro_json


def test_serialization(color_enum):
    class UserAdvance(AvroBaseModel):
        name: str
        age: int
        explicit: types.condecimal(max_digits=3, decimal_places=2)
        explicit_with_default: typing.Optional[types.condecimal(max_digits=3, decimal_places=2)] = None
        implicit: types.condecimal(max_digits=3, decimal_places=2) = decimal.Decimal("3.14")
        pets: typing.List[str] = Field(default_factory=lambda: ["dog", "cat"])
        accounts: typing.Dict[str, int] = Field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: color_enum = color_enum.BLUE
        country: str = "Argentina"
        address: str = None

        class Meta:
            schema_doc = False

    user = UserAdvance(name="bond", age=50, explicit=decimal.Decimal("3.12"))
    event = user.serialize()

    # we need to update the fields that have `types.Decimal`, otherwise the objects will be different
    assert UserAdvance.deserialize(data=event) == user


def test_not_pydantic_not_installed(monkeypatch):
    monkeypatch.setattr(utils, "pydantic", None)

    class Bus:
        pass

    assert not utils.is_pydantic_model(Bus)


def test_parse_obj():
    """
    Created nested schema resolution directly from dictionaries
    """

    class Address(AvroBaseModel):
        "An Address"

        street: str
        street_number: int

    class User(AvroBaseModel):
        "User with multiple Address"

        name: str
        age: int
        addresses: typing.List[Address]

    data_user = {
        "name": "john",
        "age": 20,
        "addresses": [
            {
                "street": "test",
                "street_number": 10,
            }
        ],
    }
    user = User.parse_obj(data_user)
    assert type(user.addresses[0]) is Address
    assert User.avro_schema()


def test_fake(color_enum) -> None:
    class Address(AvroBaseModel):
        street: str
        street_number: int

    class User(AvroBaseModel):
        name: str
        age: int
        birthday: datetime.date
        pets: typing.List[str] = Field(default_factory=lambda: ["dog", "cat"])
        accounts: typing.Dict[str, int] = Field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: color_enum = color_enum.BLUE
        country: str = "Argentina"
        address: typing.Optional[Address] = None
        role: typing.Literal["admin", "user"] = "user"

    # just calling fake is enougt to know that a proper instance was created,
    # otherwise a pydantic validation should have been raised
    User.fake()


def test_exclude_fields() -> None:
    class Message(AvroBaseModel):
        internal_field: str = Field(exclude=True)
        public_field: str

    assert Message.avro_schema()

    message = Message(internal_field="internal", public_field="public")
    assert "internal_field" not in message.dict()

    event = message.serialize(serialization_type="avro-json")

    assert Message.deserialize(event, serialization_type="avro-json") == message
    assert Message.deserialize(event, serialization_type="avro-json", create_instance=False) != message.dict()


def test_exclude_field_from_schema(user_extra_avro_attributes):
    class User(AvroBaseModel):
        "An User"

        name: str
        age: int
        last_name: str = "Bond"

        class Meta:
            namespace = "test.com.ar/user/v1"
            aliases = [
                "User",
                "My favorite User",
            ]
            exclude = [
                "last_name",
            ]

    user = User.fake()
    assert User.avro_schema() == json.dumps(user_extra_avro_attributes)
    assert User.deserialize(user.serialize()) == user
