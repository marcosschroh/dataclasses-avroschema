import json
import typing

from dataclasses_avroschema.schema_generator import SchemaGenerator


def test_one_to_one_relationship(user_one_address_schema):
    """
    Test schema relationship one-to-one
    """
    class Address:
        "An Address"
        street: str
        street_number: int

    class User:
        "An User with Address"
        name: str
        age: int
        address: Address

    user_schema = SchemaGenerator(User).avro_schema()
    assert user_schema == json.dumps(user_one_address_schema)


# def test_one_to_many_relationship(user_one_address_schema):
#     """
#     Test schema relationship one-to-one
#     """
#     class Address:
#         "An Address"
#         street: str
#         street_number: int

#     class User:
#         "An User with Address"
#         name: str
#         age: int
#         address: typing.List[Address]

#     user_schema = SchemaGenerator(User).avro_schema()
#     assert user_schema == json.dumps(user_one_address_schema)
