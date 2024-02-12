import enum
import json
import typing

import pytest

from dataclasses_avroschema import AvroModel, case, types

# casefy.camelcase('foo_bar_baz') # => "fooBarBaz"
# casefy.capitalcase('foo_bar_baz') # => "Foo_bar_baz"
# casefy.constcase('FooBarBaz') # => "_FOO_BAR_BAZ"
# casefy.lowercase('FooBarBaz') # => "foobarbaz"
# casefy.pascalcase('FooBarBaz') # => "FooBarBaz"
# casefy.pathcase('foo_bar_baz') # => "foo/bar/baz"
# casefy.snakecase('FooBarBaz') # => "foo_bar_baz"
# casefy.kebabcase('FooBarBaz') # => "-foo-bar-baz"
# casefy.upperkebabcase('FooBarBaz') # => "FOO-BAR"
# casefy.trimcase('FooBarBaz') # => "FooBarBaz"
# casefy.uppercase('FooBarBaz') # => "FOOBARBAZ"
# casefy.alphanumcase('Foo_123 Bar!') # =>'Foo123Bar'


CASE_TO_DATA = [
    (
        case.CAMELCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "eventId", "type": "string"}]}',
    ),
    (
        case.CAPITALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "Event_id", "type": "string"}]}',
    ),
    (
        case.CONSTCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EVENT_ID", "type": "string"}]}',
    ),
    (
        case.LOWERCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}]}',
    ),
    (
        case.PASCALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EventId", "type": "string"}]}',
    ),
    (
        case.PATHCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event/id", "type": "string"}]}',
    ),
    (
        case.SNAKECASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}]}',
    ),
    (
        case.SPINALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event-id", "type": "string"}]}',
    ),
    (
        case.UPPERSPINALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EVENT-ID", "type": "string"}]}',
    ),
    (
        case.TRIMCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}]}',
    ),
    (
        case.UPPERCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EVENT_ID", "type": "string"}]}',
    ),
    (
        case.ALPHANUMCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "eventid", "type": "string"}]}',
    ),
]


CASE_TO_DATA_NESTED = [
    (
        case.CAMELCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "eventId", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.CAPITALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "Event_id", "type": "string"}, {"name": "User", "type": {"type": "record", "name": "User", "fields": [{"name": "Name", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.CONSTCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EVENT_ID", "type": "string"}, {"name": "USER", "type": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.LOWERCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.PASCALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EventId", "type": "string"}, {"name": "User", "type": {"type": "record", "name": "User", "fields": [{"name": "Name", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.PATHCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event/id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.SNAKECASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.SPINALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event-id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.UPPERSPINALCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EVENT-ID", "type": "string"}, {"name": "USER", "type": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.TRIMCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "event_id", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.UPPERCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "EVENT_ID", "type": "string"}, {"name": "USER", "type": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}]}}]}',  # noqa
    ),
    (
        case.ALPHANUMCASE,
        '{"type": "record", "name": "Event", "fields": [{"name": "eventid", "type": "string"}, {"name": "user", "type": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}}]}',  # noqa
    ),
]


CASE_TO_DATA_COMPLEX_FIELDS = [
    (
        case.CAMELCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}, {"name": "favoriteColors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "hasCar", "type": "boolean", "default": false}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.CAPITALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "Name", "type": "string"}, {"name": "Age", "type": "long"}, {"name": "Pets", "type": {"type": "array", "items": "string", "name": "Pet"}}, {"name": "Accounts", "type": {"type": "map", "values": "long", "name": "Account"}}, {"name": "Md5", "type": {"type": "fixed", "name": "Md5", "size": 16}}, {"name": "Favorite_colors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "Has_car", "type": "boolean", "default": false}, {"name": "Country", "type": "string", "default": "Argentina"}, {"name": "Address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.CONSTCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "NAME", "type": "string"}, {"name": "AGE", "type": "long"}, {"name": "PETS", "type": {"type": "array", "items": "string", "name": "PET"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "long", "name": "ACCOUNT"}}, {"name": "MD_5", "type": {"type": "fixed", "name": "MD_5", "size": 16}}, {"name": "FAVORITE_COLORS", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "HAS_CAR", "type": "boolean", "default": false}, {"name": "COUNTRY", "type": "string", "default": "Argentina"}, {"name": "ADDRESS", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.LOWERCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}, {"name": "favorite_colors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "has_car", "type": "boolean", "default": false}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.PASCALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "Name", "type": "string"}, {"name": "Age", "type": "long"}, {"name": "Pets", "type": {"type": "array", "items": "string", "name": "Pet"}}, {"name": "Accounts", "type": {"type": "map", "values": "long", "name": "Account"}}, {"name": "Md5", "type": {"type": "fixed", "name": "Md5", "size": 16}}, {"name": "FavoriteColors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "HasCar", "type": "boolean", "default": false}, {"name": "Country", "type": "string", "default": "Argentina"}, {"name": "Address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.PATHCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "md/5", "type": {"type": "fixed", "name": "md/5", "size": 16}}, {"name": "favorite/colors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "has/car", "type": "boolean", "default": false}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.SNAKECASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "md_5", "type": {"type": "fixed", "name": "md_5", "size": 16}}, {"name": "favorite_colors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "has_car", "type": "boolean", "default": false}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.SPINALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "md-5", "type": {"type": "fixed", "name": "md-5", "size": 16}}, {"name": "favorite-colors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "has-car", "type": "boolean", "default": false}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.UPPERSPINALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "NAME", "type": "string"}, {"name": "AGE", "type": "long"}, {"name": "PETS", "type": {"type": "array", "items": "string", "name": "PET"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "long", "name": "ACCOUNT"}}, {"name": "MD-5", "type": {"type": "fixed", "name": "MD-5", "size": 16}}, {"name": "FAVORITE-COLORS", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "HAS-CAR", "type": "boolean", "default": false}, {"name": "COUNTRY", "type": "string", "default": "Argentina"}, {"name": "ADDRESS", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.TRIMCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}, {"name": "favorite_colors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "has_car", "type": "boolean", "default": false}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.UPPERCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "NAME", "type": "string"}, {"name": "AGE", "type": "long"}, {"name": "PETS", "type": {"type": "array", "items": "string", "name": "PET"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "long", "name": "ACCOUNT"}}, {"name": "MD5", "type": {"type": "fixed", "name": "MD5", "size": 16}}, {"name": "FAVORITE_COLORS", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "HAS_CAR", "type": "boolean", "default": false}, {"name": "COUNTRY", "type": "string", "default": "Argentina"}, {"name": "ADDRESS", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
    (
        case.ALPHANUMCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "name", "type": "string"}, {"name": "age", "type": "long"}, {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}, {"name": "accounts", "type": {"type": "map", "values": "long", "name": "account"}}, {"name": "md5", "type": {"type": "fixed", "name": "md5", "size": 16}}, {"name": "favoritecolors", "type": {"type": "enum", "name": "ColorEnum", "symbols": ["BLUE", "YELLOW", "GREEN"]}}, {"name": "hascar", "type": "boolean", "default": false}, {"name": "country", "type": "string", "default": "Argentina"}, {"name": "address", "type": ["null", "string"], "default": null}]}',  # noqa
    ),
]

CASE_TO_DATA_COMPLEX_FIELDS_NESTED = [
    (
        case.CAMELCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',  # noqa
    ),
    (
        case.CAPITALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "Users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "Name", "type": "string"}], "namespace": "types.user"}, "name": "User"}}, {"name": "Accounts", "type": {"type": "map", "values": "types.user.User", "name": "Account"}}]}',  # noqa
    ),
    (
        case.CONSTCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "USERS", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}], "namespace": "types.user"}, "name": "USER"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "types.user.User", "name": "ACCOUNT"}}]}',  # noqa
    ),
    (
        case.LOWERCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',  # noqa
    ),
    (
        case.PASCALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "Users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "Name", "type": "string"}], "namespace": "types.user"}, "name": "User"}}, {"name": "Accounts", "type": {"type": "map", "values": "types.user.User", "name": "Account"}}]}',  # noqa
    ),
    (
        case.PATHCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',  # noqa
    ),
    (
        case.SNAKECASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',  # noqa
    ),
    (
        case.SPINALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',  # noqa
    ),
    (
        case.UPPERSPINALCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "USERS", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}], "namespace": "types.user"}, "name": "USER"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "types.user.User", "name": "ACCOUNT"}}]}',  # noqa
    ),
    (
        case.TRIMCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',  # noqa
    ),
    (
        case.UPPERCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "USERS", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "NAME", "type": "string"}], "namespace": "types.user"}, "name": "USER"}}, {"name": "ACCOUNTS", "type": {"type": "map", "values": "types.user.User", "name": "ACCOUNT"}}]}',  # noqa
    ),
    (
        case.ALPHANUMCASE,
        '{"type": "record", "name": "UserAdvance", "fields": [{"name": "users", "type": {"type": "array", "items": {"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}], "namespace": "types.user"}, "name": "user"}}, {"name": "accounts", "type": {"type": "map", "values": "types.user.User", "name": "account"}}]}',  # noqa
    ),
]


@pytest.mark.parametrize("case_type, schema", CASE_TO_DATA)
def test_case_record(case_type, schema):
    class Event(AvroModel):
        event_id: str

        class Meta:
            schema_doc = False

    assert schema == Event.avro_schema(case_type=case_type)
    assert json.loads(schema) == Event.avro_schema_to_python(case_type=case_type)


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
    assert json.loads(schema) == Event.avro_schema_to_python(case_type=case_type)


@pytest.mark.parametrize("case_type, schema", CASE_TO_DATA_COMPLEX_FIELDS)
def test_case_complex_fields(case_type, schema):
    class ColorEnum(enum.Enum):
        BLUE = "BLUE"
        YELLOW = "YELLOW"
        GREEN = "GREEN"

    class UserAdvance(AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        md5: types.confixed(size=16)
        favorite_colors: ColorEnum
        has_car: bool = False
        country: str = "Argentina"
        address: str = None

        class Meta:
            schema_doc = False

    assert schema == UserAdvance.avro_schema(case_type=case_type)
    assert json.loads(schema) == UserAdvance.avro_schema_to_python(case_type=case_type)


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
    assert json.loads(schema) == UserAdvance.avro_schema_to_python(case_type=case_type)
