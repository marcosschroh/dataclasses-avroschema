from fastavro import parse_schema

from dataclasses_avroschema.schema_generator import SchemaGenerator


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
    schema = SchemaGenerator(user_dataclass).to_python()

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
    schema = SchemaGenerator(user_extra_avro_atributes_dataclass).to_python()

    assert parse_schema(schema)


def test_advance_schema(user_advance_dataclass):
    """
    Python class contains the primitive, primitive with default values
    array, enum, map types.

    class UserAdvance:
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        has_car: bool = False
        favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
        country: str = "Argentina"
        address: str = None
    """
    schema = SchemaGenerator(user_advance_dataclass).to_python()

    assert parse_schema(schema)

