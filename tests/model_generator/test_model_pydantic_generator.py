from dataclasses_avroschema import BaseClassEnum, ModelGenerator, types


def test_pydantic_model(schema_one_to_many_map_relationship: types.JsonDict) -> None:
    expected_result = """
from pydantic import BaseModel
import typing



class Address(BaseModel):
    street: str
    street_number: int

    class Meta:
        schema_doc = "An Address"



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
    friend: typing.Optional[typing.Type["User"]] = None
    relatives: typing.List[typing.Type["User"]] = Field(default_factory=list)
    teammates: typing.Dict[str, typing.Type["User"]] = Field(default_factory=dict)
"""
    model_generator = ModelGenerator(base_class=BaseClassEnum.PYDANTIC_MODEL.value)
    result = model_generator.render(schema=schema_one_to_self_relationship)
    assert result.strip() == expected_result.strip()


def test_avro_pydantic_model(schema_one_to_many_map_relationship: types.JsonDict) -> None:
    expected_result = """
from dataclasses_avroschema.avrodantic import AvroBaseModel
import typing



class Address(AvroBaseModel):
    street: str
    street_number: int

    class Meta:
        schema_doc = "An Address"



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
    friend: typing.Optional[typing.Type["User"]] = None
    relatives: typing.List[typing.Type["User"]] = Field(default_factory=list)
    teammates: typing.Dict[str, typing.Type["User"]] = Field(default_factory=dict)

"""
    model_generator = ModelGenerator(base_class=BaseClassEnum.AVRO_DANTIC_MODEL.value)
    result = model_generator.render(schema=schema_one_to_self_relationship)
    assert result.strip() == expected_result.strip()
