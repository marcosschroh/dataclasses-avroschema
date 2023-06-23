from dataclasses_avroschema import BaseClassEnum, ModelGenerator, types
from dataclasses_avroschema.fields import field_utils
from dataclasses_avroschema.model_generator.avro_to_python_utils import render_datetime


def test_pydantic_model(schema_one_to_many_map_relationship: types.JsonDict) -> None:
    expected_result = """
from pydantic import BaseModel
import typing



class Address(BaseModel):
    \"""
    An Address
    \"""
    street: str
    street_number: int



class User(BaseModel):
    name: str
    age: int
    addresses: typing.Dict[str, Address]
    crazy_union: typing.Union[str, typing.Dict[str, Address]]
    optional_addresses: typing.Optional[typing.Dict[str, Address]] = None
"""
    model_generator = ModelGenerator(base_class=BaseClassEnum.PYDANTIC_MODEL.value)
    result = model_generator.render(schema=schema_one_to_many_map_relationship)
    assert result.strip() == expected_result.strip()


def test_pydantic_model_with_meta_fields(schema_one_to_self_relationship: types.JsonDict) -> None:
    expected_result = """
from pydantic import BaseModel
from pydantic import Field
import typing



class User(BaseModel):
    name: str
    age: int
    friend: typing.Optional["User"] = None
    relatives: typing.List["User"] = Field(default_factory=list)
    teammates: typing.Dict[str, "User"] = Field(default_factory=dict)
"""
    model_generator = ModelGenerator(base_class=BaseClassEnum.PYDANTIC_MODEL.value)
    result = model_generator.render(schema=schema_one_to_self_relationship)
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_model(schema_one_to_many_map_relationship: types.JsonDict) -> None:
    expected_result = """
from dataclasses_avroschema.avrodantic import AvroBaseModel
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
    optional_addresses: typing.Optional[typing.Dict[str, Address]] = None
"""
    model_generator = ModelGenerator(base_class=BaseClassEnum.AVRO_DANTIC_MODEL.value)
    result = model_generator.render(schema=schema_one_to_many_map_relationship)
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_model_with_meta_fields(schema_one_to_self_relationship: types.JsonDict) -> None:
    expected_result = """
from dataclasses_avroschema.avrodantic import AvroBaseModel
from pydantic import Field
import typing



class User(AvroBaseModel):
    name: str
    age: int
    friend: typing.Optional["User"] = None
    relatives: typing.List["User"] = Field(default_factory=list)
    teammates: typing.Dict[str, "User"] = Field(default_factory=dict)
"""
    model_generator = ModelGenerator(base_class=BaseClassEnum.AVRO_DANTIC_MODEL.value)
    result = model_generator.render(schema=schema_one_to_self_relationship)
    assert result.strip() == expected_result.strip()


def test_decimal_field(schema_with_decimal_field: types.JsonDict) -> None:
    expected_result = """
from dataclasses_avroschema.avrodantic import AvroBaseModel
from pydantic import condecimal



class Demo(AvroBaseModel):
    foo: condecimal(max_digits=10, decimal_places=3)
"""
    model_generator = ModelGenerator(base_class=BaseClassEnum.AVRO_DANTIC_MODEL.value)
    result = model_generator.render(schema=schema_with_decimal_field)
    assert result.strip() == expected_result.strip()


def test_schema_logical_types(schema_with_logical_types: types.JsonDict) -> None:
    release_datetime = render_datetime(value=1570903062000, format=field_utils.TIMESTAMP_MILLIS)
    release_datetime_micro = render_datetime(value=1570903062000000, format=field_utils.TIMESTAMP_MICROS)

    expected_result = f"""
from dataclasses_avroschema import types
from dataclasses_avroschema.avrodantic import AvroBaseModel
from pydantic import condecimal
import datetime
import decimal
import pydantic
import typing



class LogicalTypes(AvroBaseModel):
    birthday: datetime.date
    birthday_time: datetime.time
    birthday_datetime: datetime.datetime
    uuid_1: pydantic.UUID4
    money: condecimal(max_digits=3, decimal_places=2)
    meeting_date: typing.Optional[datetime.date] = None
    release_date: datetime.date = datetime.date(2019, 10, 12)
    meeting_time: typing.Optional[datetime.time] = None
    release_time: datetime.time = datetime.time(17, 57, 42)
    release_time_micro: types.TimeMicro = datetime.time(17, 57, 42, 0)
    meeting_datetime: typing.Optional[datetime.datetime] = None
    release_datetime: datetime.datetime = {release_datetime}
    release_datetime_micro: types.DateTimeMicro = {release_datetime_micro}
    uuid_2: typing.Optional[pydantic.UUID4] = None
    event_uuid: pydantic.UUID4 = "ad0677ab-bd1c-4383-9d45-e46c56bcc5c9"
    explicit_with_default: condecimal(max_digits=3, decimal_places=2) = decimal.Decimal('3.14')

"""
    model_generator = ModelGenerator(base_class=BaseClassEnum.AVRO_DANTIC_MODEL.value)
    result = model_generator.render(schema=schema_with_logical_types)
    assert result.strip() == expected_result.strip()
