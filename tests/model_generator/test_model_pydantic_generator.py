from dataclasses_avroschema import ModelGenerator, ModelType, types
from dataclasses_avroschema.fields import field_utils
from dataclasses_avroschema.model_generator.lang.python.avro_to_python_utils import (
    render_datetime,
)


def test_pydantic_model(schema_one_to_many_map_relationship: types.JsonDict) -> None:
    expected_result = """
import pydantic
import typing



class Address(pydantic.BaseModel):
    \"""
    An Address
    \"""
    street: str
    street_number: int



class User(pydantic.BaseModel):
    name: str
    age: int
    addresses: typing.Dict[str, Address]
    crazy_union: typing.Union[str, typing.Dict[str, Address]]
    default_address: Address = pydantic.Field(default_factory=lambda: Address(**{'street': 'Main Street', 'street_number': 10}))
    optional_addresses: typing.Optional[typing.Dict[str, Address]] = None
"""  # noqa: E501
    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_one_to_many_map_relationship, model_type=ModelType.PYDANTIC.value)
    assert result.strip() == expected_result.strip()


def test_pydantic_model_with_meta_fields(
    schema_one_to_self_relationship: types.JsonDict,
) -> None:
    expected_result = """
import pydantic
import typing



class User(pydantic.BaseModel):
    name: str
    age: int
    friend: typing.Optional["User"] = None
    relatives: typing.List["User"] = pydantic.Field(default_factory=list)
    teammates: typing.Dict[str, "User"] = pydantic.Field(default_factory=dict)
"""
    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_one_to_self_relationship, model_type=ModelType.PYDANTIC.value)
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_model(
    schema_one_to_many_map_relationship: types.JsonDict,
) -> None:
    expected_result = """
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic
import typing



class Address(AvroBaseModel):
    \"""
    An Address
    \"""
    street: str
    street_number: int



class User(AvroBaseModel):
    name: str
    age: int
    addresses: typing.Dict[str, Address]
    crazy_union: typing.Union[str, typing.Dict[str, Address]]
    default_address: Address = pydantic.Field(default_factory=lambda: Address(**{'street': 'Main Street', 'street_number': 10}))
    optional_addresses: typing.Optional[typing.Dict[str, Address]] = None
"""  # noqa: E501
    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_one_to_many_map_relationship, model_type=ModelType.AVRODANTIC.value)
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_invalid_python_identifiers(schema_with_invalid_python_identifiers: types.JsonDict) -> None:
    expected_result = """
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic



class Address(AvroBaseModel):
    \"""
    An Address
    \"""
    street_name: str = pydantic.Field(metadata={'aliases': ['street-name']})
    street_number: int = pydantic.Field(metadata={'aliases': ['street-number']})
    street_zipcode: str = pydantic.Field(metadata={'aliases': ['zipcode', 'street-zipcode']})
    city_name: str = pydantic.Field(metadata={'aliases': ['city-name']})
    ValidIdentifier: str
    anotherIdentifier: str
    _private: str


"""
    model_generator = ModelGenerator()
    result = model_generator.render(
        schema=schema_with_invalid_python_identifiers, model_type=ModelType.AVRODANTIC.value
    )
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_python_keywords(schema_with_python_keywords: types.JsonDict) -> None:
    expected_result = """
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic



class Address(AvroBaseModel):
    \"""
    An Address
    \"""
    class_: str = pydantic.Field(metadata={'aliases': ['class']})
    yield_: str = pydantic.Field(metadata={'aliases': ['yield']})
    yield_class: int


"""
    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_with_python_keywords, model_type=ModelType.AVRODANTIC.value)
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_model_with_meta_fields(
    schema_one_to_self_relationship: types.JsonDict,
) -> None:
    expected_result = """
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic
import typing



class User(AvroBaseModel):
    name: str
    age: int
    friend: typing.Optional["User"] = None
    relatives: typing.List["User"] = pydantic.Field(default_factory=list)
    teammates: typing.Dict[str, "User"] = pydantic.Field(default_factory=dict)
"""
    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_one_to_self_relationship, model_type=ModelType.AVRODANTIC.value)
    assert result.strip() == expected_result.strip()


def test_pydantic_with_fields_with_metadata(
    with_fields_with_metadata: types.JsonDict,
) -> None:
    expected_result = """
import pydantic



class Message(pydantic.BaseModel):
    someotherfield: int = pydantic.Field(metadata={'aliases': ['oldname'], 'avro.java.string': 'String'}, description="test")
    fieldwithdoc: int = pydantic.Field(description="test")
    fieldwithdefault: str = pydantic.Field(metadata={'avro.java.string': 'String'}, default="some default value")

    
    class Meta:
        field_order = ['fieldwithdefault', 'someotherfield', 'fieldwithdoc']

"""  # noqa: E501
    model_generator = ModelGenerator()
    result = model_generator.render(schema=with_fields_with_metadata, model_type=ModelType.PYDANTIC.value)
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_primitive_types_as_defined_types(
    schema_primitive_types_as_defined_types: types.JsonDict,
) -> None:
    expected_result = """
from dataclasses_avroschema import types
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic
import typing



class Address(AvroBaseModel):
    street: str
    name: typing.Optional[str]
    weight: types.Int32 = pydantic.Field(metadata={'unit': 'kg'})
    pet_age: types.Int32 = 1
    expirience: types.Int32 = pydantic.Field(metadata={'unit': 'years'}, default=10)
    second_street: str = pydantic.Field(metadata={'avro.java.string': 'String'}, default="Batman")
    reason: typing.Optional[str] = pydantic.Field(metadata={'avro.java.string': 'String'}, default=None)

"""
    model_generator = ModelGenerator()
    result = model_generator.render(
        schema=schema_primitive_types_as_defined_types, model_type=ModelType.AVRODANTIC.value
    )
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_with_fields_with_metadata(
    with_fields_with_metadata: types.JsonDict,
) -> None:
    expected_result = """
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic



class Message(AvroBaseModel):
    someotherfield: int = pydantic.Field(metadata={'aliases': ['oldname'], 'avro.java.string': 'String'}, description="test")
    fieldwithdoc: int = pydantic.Field(description="test")
    fieldwithdefault: str = pydantic.Field(metadata={'avro.java.string': 'String'}, default="some default value")

    
    class Meta:
        field_order = ['fieldwithdefault', 'someotherfield', 'fieldwithdoc']

"""  # noqa: E501
    model_generator = ModelGenerator()
    result = model_generator.render(schema=with_fields_with_metadata, model_type=ModelType.AVRODANTIC.value)
    assert result.strip() == expected_result.strip()


def test_decimal_field(schema_with_decimal_field: types.JsonDict) -> None:
    expected_result = """
from dataclasses_avroschema import types
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic



class Demo(AvroBaseModel):
    foo: types.condecimal(max_digits=10, decimal_places=3)

    
    class Meta:
        schema_name = "demo"
"""
    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_with_decimal_field, model_type=ModelType.AVRODANTIC.value)
    assert result.strip() == expected_result.strip()


def test_schema_logical_types(schema_with_logical_types: types.JsonDict) -> None:
    release_datetime = render_datetime(value=1570903062000, format=field_utils.TIMESTAMP_MILLIS)
    release_datetime_micro = render_datetime(value=1570903062000000, format=field_utils.TIMESTAMP_MICROS)

    expected_result = f"""
from dataclasses_avroschema import types
from dataclasses_avroschema.pydantic import AvroBaseModel
import datetime
import decimal
import pydantic
import typing
import uuid



class LogicalTypes(AvroBaseModel):
    birthday: datetime.date
    birthday_time: datetime.time
    birthday_datetime: datetime.datetime
    uuid_1: uuid.UUID
    money: types.condecimal(max_digits=3, decimal_places=2)
    meeting_date: typing.Optional[datetime.date] = None
    release_date: datetime.date = datetime.date(2019, 10, 12)
    meeting_time: typing.Optional[datetime.time] = None
    release_time: datetime.time = datetime.time(17, 57, 42)
    release_time_micro: types.TimeMicro = datetime.time(17, 57, 42, 0)
    meeting_datetime: typing.Optional[datetime.datetime] = None
    release_datetime: datetime.datetime = {release_datetime}
    release_datetime_micro: types.DateTimeMicro = {release_datetime_micro}
    time_elapsed: datetime.timedelta = datetime.timedelta(seconds=788645.006007)
    uuid_2: typing.Optional[uuid.UUID] = None
    event_uuid: uuid.UUID = "ad0677ab-bd1c-4383-9d45-e46c56bcc5c9"
    explicit_with_default: types.condecimal(max_digits=3, decimal_places=2) = decimal.Decimal('3.14')

"""
    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_with_logical_types, model_type=ModelType.AVRODANTIC.value)
    assert result.strip() == expected_result.strip()


def test_schema_with_pydantic_fields(schema_with_pydantic_fields):
    expected_result = """
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic
import typing



class Infrastructure(AvroBaseModel):
    email: pydantic.EmailStr
    postgres_dsn: pydantic.PostgresDsn
    cockroach_dsn: pydantic.CockroachDsn
    amqp_dsn: pydantic.AmqpDsn
    redis_dsn: pydantic.RedisDsn
    mongo_dsn: pydantic.MongoDsn
    kafka_url: pydantic.KafkaDsn
    total_nodes: pydantic.PositiveInt
    event_id: pydantic.UUID3
    landing_zone_nodes: typing.List[pydantic.PositiveInt]
    total_nodes_in_aws: pydantic.PositiveInt = 10
    optional_kafka_url: typing.Optional[pydantic.KafkaDsn] = None

"""

    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_with_pydantic_fields, model_type=ModelType.AVRODANTIC.value)
    assert result.strip() == expected_result.strip()


def test_schema_with_pydantic_constrained_field(
    schema_with_pydantic_constrained_fields,
):
    expected_result = """
from dataclasses_avroschema import types
from dataclasses_avroschema.pydantic import AvroBaseModel
import pydantic



class ConstrainedValues(AvroBaseModel):
    constrained_int: pydantic.conint(gt=10, lt=20)

"""

    model_generator = ModelGenerator()
    result = model_generator.render(
        schema=schema_with_pydantic_constrained_fields, model_type=ModelType.AVRODANTIC.value
    )
    assert result.strip() == expected_result.strip()


def test_schema_with_pydantic_logical_fields(schema_with_pydantic_logical_fields):
    expected_result = """
from dataclasses_avroschema.pydantic import AvroBaseModel
import datetime
import pydantic
import uuid



class LogicalTypesPydantic(AvroBaseModel):
    \"""
    Some logical types
    \"""
    birthday: datetime.date = datetime.date(2019, 10, 12)
    meeting_time: datetime.time = datetime.time(17, 57, 42)
    release_datetime: datetime.datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)
    past_date: pydantic.PastDate = datetime.date(2019, 10, 12)
    future_date: pydantic.FutureDate = datetime.date(9999, 12, 31)
    past_datetime: pydantic.PastDatetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)
    future_datetime: pydantic.FutureDatetime = datetime.datetime(9999, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
    aware_datetime: pydantic.AwareDatetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)
    naive_datetime: pydantic.NaiveDatetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)
    event_uuid: uuid.UUID = "09f00184-7721-4266-a955-21048a5cc235"

"""
    model_generator = ModelGenerator()
    result = model_generator.render(schema=schema_with_pydantic_logical_fields, model_type=ModelType.AVRODANTIC.value)
    assert result.strip() == expected_result.strip()
