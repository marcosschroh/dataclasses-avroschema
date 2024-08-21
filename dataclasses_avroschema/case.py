import typing

import casefy

from .fields.field_utils import ENUM

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

CAMELCASE = "camelcase"
CAPITALCASE = "capitalcase"
CONSTCASE = "constcase"
LOWERCASE = "lowercase"
PASCALCASE = "pascalcase"
PATHCASE = "PATHCASE"
SNAKECASE = "snakecase"
SPINALCASE = "spinalcase"
UPPERSPINALCASE = "upperkebabcase"
TRIMCASE = "trimcase"
UPPERCASE = "uppercase"
ALPHANUMCASE = "alphanumcase"


CASE_TO_FUNC = {
    CAMELCASE: casefy.camelcase,
    CAPITALCASE: casefy.capitalcase,
    CONSTCASE: casefy.constcase,
    LOWERCASE: casefy.lowercase,
    PASCALCASE: casefy.pascalcase,
    PATHCASE: lambda value: casefy.separatorcase(value, separator="/"),
    SNAKECASE: casefy.snakecase,
    SPINALCASE: casefy.kebabcase,
    UPPERSPINALCASE: casefy.upperkebabcase,
    TRIMCASE: str.strip,
    UPPERCASE: casefy.uppercase,
    ALPHANUMCASE: casefy.alphanumcase,
}


def case_item(item: typing.Dict, case_type: str) -> typing.Dict:
    case_func = CASE_TO_FUNC[case_type]
    new_field = {}
    for key, value in item.items():
        if key == "name":
            case_name = case_func(value)  # type: ignore
            new_field[key] = case_name
        elif isinstance(value, dict) and value.get("name"):
            # means that it is a complex type with a record
            new_record = case_record(value, case_type=case_type)
            new_field[key] = new_record
        elif isinstance(value, list):
            new_field[key] = [
                case_record(element, case_type=case_type) if isinstance(element, dict) else element for element in value
            ]
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
