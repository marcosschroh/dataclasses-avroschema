import typing

import pytest

from dataclasses_avroschema import AvroModel, case, types

# Summary from https://github.com/okunishinishi/python-stringcase
# stringcase.camelcase('foo_bar_baz') # => "fooBarBaz"
# stringcase.capitalcase('foo_bar_baz') # => "Foo_bar_baz"
# stringcase.constcase('FooBarBaz') # => "_FOO_BAR_BAZ"
# stringcase.lowercase('FooBarBaz') # => "foobarbaz"
# stringcase.pascalcase('FooBarBaz') # => "FooBarBaz"
# stringcase.pathcase('foo_bar_baz') # => "foo/bar/baz"
# stringcase.snakecase('FooBarBaz') # => "foo_bar_baz"
# stringcase.spinalcase('FooBarBaz') # => "-foo-bar-baz"
# stringcase.trimcase('FooBarBaz') # => "FooBarBaz"
# stringcase.uppercase('FooBarBaz') # => "FOOBARBAZ"
# stringcase.alphanumcase('Foo_123 Bar!') # =>'Foo123Bar'


CASE_TO_DATA = [
    (case.CAMELCASE, '{"type": "record", "name": "Event", "fields": [{"name": "eventId", "type": "string"}]}'),
    (case.CAPITALCASE, '{"type": "record", "name": "Event", "fields": [{"name": "Event_id", "type": "string"}]}'),
    (case.CONSTCASE, '{"type": "record", "name": "Event", "fields": [{"name": "EVENT_ID", "type": "string"}]}'),
    (case.LOWERCASE, '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}]}'),
    (case.PASCALCASE, '{"type": "record", "name": "Event", "fields": [{"name": "EventId", "type": "string"}]}'),
    (case.PATHCASE, '{"type": "record", "name": "Event", "fields": [{"name": "event/id", "type": "string"}]}'),
    (case.SNAKECASE, '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}]}'),
    (case.SPINALCASE, '{"type": "record", "name": "Event", "fields": [{"name": "event-id", "type": "string"}]}'),
    (case.TRIMCASE, '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}]}'),
    (case.UPPERCASE, '{"type": "record", "name": "Event", "fields": [{"name": "EVENT_ID", "type": "string"}]}'),
    (case.ALPHANUMCASE, '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}]}'),
]


CASE_TO_DATA_NESTED = [
    (
        case.CAMELCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "eventId", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',
    ),
    (
        case.CAPITALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "Event_id", "type": "string"}, {"name": "User", "type": {"type": "record", "name": "User", "fields": [{"name": "Name", "type": "string"}]}}]}',
    ),
    (
        case.CONSTCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EVENT_ID", "type": "string"}, {"name": "USER", "type": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}]}}]}',
    ),
    (
        case.LOWERCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',
    ),
    (
        case.PASCALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EventId", "type": "string"}, {"name": "User", "type": {"type": "record", "name": "User", "fields": [{"name": "Name", "type": "string"}]}}]}',
    ),
    (
        case.PATHCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event/id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',
    ),
    (
        case.SNAKECASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',
    ),
    (
        case.SPINALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event-id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',
    ),
    (
        case.TRIMCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',
    ),
    (
        case.UPPERCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EVENT_ID", "type": "string"}, {"name": "USER", "type": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}]}}]}',
    ),
    (
        case.ALPHANUMCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',
    ),
]


CASE_TO_DATA_COMPLEX_FIELDS = [
    (
        case.CAMELCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "hasCar", "type": "boolean", "default": false}, {"name": "favoriteColors", "type": {"type": "enum", "name": "favoriteColor", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}]}',
    ),
    (
        case.CAPITALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "Name", "type": "string"}, {"name": "Age", "type": "long"}, {"name": "Pets", "type": {"type": "array", "items": "string", "name": "Pet"}}, {"name": "Accounts", "type": {"type": "map", "values": "long", "name": "Account"}}, {"name": "Has_car", "type": "boolean", "default": false}, {"name": "Favorite_colors", "type": {"type": "enum", "name": "Favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "Country", "type": "string", "default": "Argentina"}, {"name": "Address", "type": ["null", "string"], "default": null}, {"name": "Md5", "type": {"type": "fixed", "name": "Md5", "size": 16}}]}',
    ),
    (
        case.CONSTCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "NAME", "type": "string"}, {"name": "AGE", "type": "long"}, {"name": "PETS", "type": {"type": "array", "items": "string", "name": "PET"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "long", "name": "ACCOUNT"}}, {"name": "HAS_CAR", "type": "boolean", "default": false}, {"name": "FAVORITE_COLORS", "type": {"type": "enum", "name": "FAVORITE_COLOR", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "COUNTRY", "type": "string", "default": "Argentina"}, {"name": "ADDRESS", "type": ["null", "string"], "default": null}, {"name": "MD5", "type": {"type": "fixed", "name": "MD5", "size": 16}}]}',
    ),
    (
        case.LOWERCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "has_car", "type": "boolean", "default": false}, {"name": "favorite_colors", "type": {"type": "enum", "name": "favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}]}',
    ),
    (
        case.PASCALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "Name", "type": "string"}, {"name": "Age", "type": "long"}, {"name": "Pets", "type": {"type": "array", "items": "string", "name": "Pet"}}, {"name": "Accounts", "type": {"type": "map", "values": "long", "name": "Account"}}, {"name": "HasCar", "type": "boolean", "default": false}, {"name": "FavoriteColors", "type": {"type": "enum", "name": "FavoriteColor", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "Country", "type": "string", "default": "Argentina"}, {"name": "Address", "type": ["null", "string"], "default": null}, {"name": "Md5", "type": {"type": "fixed", "name": "Md5", "size": 16}}]}',
    ),
    (
        case.PATHCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "has/car", "type": "boolean", "default": false}, {"name": "favorite/colors", "type": {"type": "enum", "name": "favorite/color", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}]}',
    ),
    (
        case.SNAKECASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "has_car", "type": "boolean", "default": false}, {"name": "favorite_colors", "type": {"type": "enum", "name": "favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}]}',
    ),
    (
        case.SPINALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "has-car", "type": "boolean", "default": false}, {"name": "favorite-colors", "type": {"type": "enum", "name": "favorite-color", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}]}',
    ),
    (
        case.TRIMCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "has_car", "type": "boolean", "default": false}, {"name": "favorite_colors", "type": {"type": "enum", "name": "favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}]}',
    ),
    (
        case.UPPERCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "NAME", "type": "string"}, {"name": "AGE", "type": "long"}, {"name": "PETS", "type": {"type": "array", "items": "string", "name": "PET"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "long", "name": "ACCOUNT"}}, {"name": "HAS_CAR", "type": "boolean", "default": false}, {"name": "FAVORITE_COLORS", "type": {"type": "enum", "name": "FAVORITE_COLOR", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "COUNTRY", "type": "string", "default": "Argentina"}, {"name": "ADDRESS", "type": ["null", "string"], "default": null}, {"name": "MD5", "type": {"type": "fixed", "name": "MD5", "size": 16}}]}',
    ),
    (
        case.ALPHANUMCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "has_car", "type": "boolean", "default": false}, {"name": "favorite_colors", "type": {"type": "enum", "name": "favorite_color", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}]}',
    ),
]

CASE_TO_DATA_COMPLEX_FIELDS_NESTED = [
    (
        case.CAMELCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',
    ),
    (
        case.CAPITALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "Users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "Name", "type": "string"}], "namespace": "types.user"}, "name": "User"}}, {"name": "Accounts", "type": {"type": "map", "values": "types.user.User", "name": "Account"}}]}',
    ),
    (
        case.CONSTCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "USERS", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}], "namespace": "types.user"}, "name": "USER"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "types.user.User", "name": "ACCOUNT"}}]}',
    ),
    (
        case.LOWERCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',
    ),
    (
        case.PASCALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "Users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "Name", "type": "string"}], "namespace": "types.user"}, "name": "User"}}, {"name": "Accounts", "type": {"type": "map", "values": "types.user.User", "name": "Account"}}]}',
    ),
    (
        case.PATHCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',
    ),
    (
        case.SNAKECASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',
    ),
    (
        case.SPINALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',
    ),
    (
        case.TRIMCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',
    ),
    (
        case.UPPERCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "USERS", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}], "namespace": "types.user"}, "name": "USER"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "types.user.User", "name": "ACCOUNT"}}]}',
    ),
    (
        case.ALPHANUMCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',
    ),
]


@pytest.mark.parametrize("case_type, schema", CASE_TO_DATA)
def test_case_record(case_type, schema):
    class Event(AvroModel):
        event_id: str

        class Meta:
            schema_doc = False

    assert schema == Event.avro_schema(case_type=case_type)


@pytest.mark.parametrize("case_type, schema", CASE_TO_DATA_NESTED)
def test_case_nested_records(case_type, schema):
    class User(AvroModel):
        name: str

        class Meta:
            schema_doc = False

    class Event(AvroModel):
        event_id: str
        user: User

        class Meta:
            schema_doc = False

    assert schema == Event.avro_schema(case_type=case_type)


@pytest.mark.parametrize("case_type, schema", CASE_TO_DATA_COMPLEX_FIELDS)
def test_case_complex_fields(case_type, schema):
    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        has_car: bool = False
        favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"])
        country: str = "Argentina"
        address: str = None
        md5: types.Fixed = types.Fixed(16)

        class Meta:
            schema_doc = False

    assert schema == UserAdvance.avro_schema(case_type=case_type)


@pytest.mark.parametrize("case_type, schema", CASE_TO_DATA_COMPLEX_FIELDS_NESTED)
def test_case_complex_fields_nested(case_type, schema):
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

    assert schema == UserAdvance.avro_schema(case_type=case_type)
