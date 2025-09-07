import sys
from string import Template

PYTHON_VERSION_GE_311 = sys.version_info.major == 3 and sys.version_info.minor >= 11

FIELD_TYPE_TEMPLATE = "$name: $type"
METACLASS_FIELD_TEMPLATE = '$name = "$value"'
METACLASS_ALIAS_FIELD = "$name = $value"
METACLASS_SCHEMA_FIELD = '$name = """$schema"""'
METACLASS_DECORATOR = "@enum.nonmember" if PYTHON_VERSION_GE_311 else ""
FIELD_DEFAULT_TEMPLATE = " = $default"
OPTIONAL_TEMPLATE = "typing.Optional[$type]"
UNION_TEMPLATE = "typing.Union[$type]"
LIST_TEMPLATE = "typing.List[$type]"
DICT_TEMPLATE = "typing.Dict[str, $type]"
FIXED_TEMPLATE = "types.confixed($properties)"
FIELD_TEMPLATE = "dataclasses.field($properties)"
TYPE_TEMPLATE = '"$type"'
DATE_TEMPLATE = "datetime.date($year, $month, $day)"
TIME_TEMPLATE = "datetime.time($hour, $minute, $second)"
TIME_MICROS_TEMPLATE = "datetime.time($hour, $minute, $second, $microsecond)"
DATETIME_TEMPLATE = "datetime.datetime($year, $month, $day, $hour, $minute, $second, tzinfo=datetime.timezone.utc)"
DATETIME_MICROS_TEMPLATE = (
    "datetime.datetime($year, $month, $day, $hour, $minute, $second, $microsecond, tzinfo=datetime.timezone.utc)"
)
TIMEDELTA_TEMPLATE = "datetime.timedelta(seconds=$seconds)"
DECIMAL_TEMPLATE = "decimal.Decimal('$value')"
DECIMAL_TYPE_TEMPLATE = "types.condecimal(max_digits=$precision, decimal_places=$scale)"

ENUM_SYMBOL_TEMPLATE = "$key = $value"
ENUM_PYTHON_VERSION = "str, enum.Enum" if PYTHON_VERSION_GE_311 else "enum.Enum"
ENUM_TEMPLATE = f"""
class $name({ENUM_PYTHON_VERSION}):$docstring
    $symbols
"""

CLASS_TEMPLATE = """
$decorator
class $name($base_class):$docstring
    $fields
"""

DOCSTRINGS_WITH_FIELDS_TEMPLATE = '''
    """
    $class_docstring
    Attributes:
        $fields_docstring
    """
'''

INSTANCE_TEMPLATE = "$type($properties)"

METACLASS_TEMPLATE = """
$decorator
class Meta:
    $properties
"""

IMPORTS_TEMPLATE = """
$imports
"""

MODULE_TEMPLATE = """
$imports
$extras
$classes
"""

# Pydanntic specific
PYDANTIC_FIELD = "pydantic.Field($properties)"

field_type_template = Template(FIELD_TYPE_TEMPLATE)
metaclass_field_template = Template(METACLASS_FIELD_TEMPLATE)
metaclass_alias_field_template = Template(METACLASS_ALIAS_FIELD)
metaclass_schema_field_template = Template(METACLASS_SCHEMA_FIELD)
field_default_template = Template(FIELD_DEFAULT_TEMPLATE)
optional_template = Template(OPTIONAL_TEMPLATE)
union_template = Template(UNION_TEMPLATE)
list_template = Template(LIST_TEMPLATE)
dict_template = Template(DICT_TEMPLATE)
fixed_template = Template(FIXED_TEMPLATE)
decimal_template = Template(DECIMAL_TEMPLATE)
decimal_type_template = Template(DECIMAL_TYPE_TEMPLATE)
enum_symbol_template = Template(ENUM_SYMBOL_TEMPLATE)
enum_template = Template(ENUM_TEMPLATE)
field_template = Template(FIELD_TEMPLATE)
pydantic_field_template = Template(PYDANTIC_FIELD)
docstrings_with_fields_template = Template(DOCSTRINGS_WITH_FIELDS_TEMPLATE)
class_template = Template(CLASS_TEMPLATE)
instance_template = Template(INSTANCE_TEMPLATE)
metaclass_template = Template(METACLASS_TEMPLATE)
type_template = Template(TYPE_TEMPLATE)
date_template = Template(DATE_TEMPLATE)
time_template = Template(TIME_TEMPLATE)
time_micros_template = Template(TIME_MICROS_TEMPLATE)
datetime_template = Template(DATETIME_TEMPLATE)
datetime_micros_template = Template(DATETIME_MICROS_TEMPLATE)
timedelta_template = Template(TIMEDELTA_TEMPLATE)
imports_template = Template(IMPORTS_TEMPLATE.strip())
module_template = Template(MODULE_TEMPLATE.strip())
