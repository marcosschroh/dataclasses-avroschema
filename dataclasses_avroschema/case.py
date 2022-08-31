import typing

import stringcase

from .field_utils import ENUM

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

CAMELCASE = "camelcase"
CAPITALCASE = "capitalcase"
CONSTCASE = "constcase"
LOWERCASE = "lowercase"
PASCALCASE = "pascalcase"
PATHCASE = "PATHCASE"
SNAKECASE = "snakecase"
SPINALCASE = "spinalcase"
TRIMCASE = "trimcase"
UPPERCASE = "uppercase"
ALPHANUMCASE = "alphanumcase"


CASE_TO_FUNC = {
    CAMELCASE: stringcase.camelcase,
    CAPITALCASE: stringcase.capitalcase,
    CONSTCASE: stringcase.constcase,
    LOWERCASE: stringcase.lowercase,
    PASCALCASE: stringcase.pascalcase,
    PATHCASE: stringcase.pathcase,
    SNAKECASE: stringcase.snakecase,
    SPINALCASE: stringcase.spinalcase,
    TRIMCASE: stringcase.trimcase,
    UPPERCASE: stringcase.uppercase,
    ALPHANUMCASE: stringcase.alphanumcase,
}


def case_item(item: typing.Dict, case_type: str) -> typing.Dict:
    case_func = CASE_TO_FUNC[case_type]
    new_field = {}
    for key, value in item.items():
        if key == "name":
            case_name = case_func(value)
            new_field[key] = case_name
        elif isinstance(value, dict) and value.get("name"):
            # means that it is a complex type with a record
            new_record = case_record(value, case_type=case_type)
            new_field[key] = new_record
        else:
            new_field[key] = value

    return new_field


def case_record(avro_schema_dict: typing.Dict, case_type: str) -> typing.Dict:
    fields = avro_schema_dict.get("fields")

    if fields is not None:
        new_fields = []
        for field in fields:
            new_field = case_item(field, case_type)
            new_fields.append(new_field)
        avro_schema_dict["fields"] = new_fields
        return avro_schema_dict
    elif avro_schema_dict["type"] == ENUM:
        # enums should not be case, like records
        return avro_schema_dict
    else:
        return case_item(avro_schema_dict, case_type)
