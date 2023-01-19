from string import Template

FIELD_TEMPLATE = "$name: $type"
METACLASS_FIELD_TEMPLATE = '$name = "$value"'
METACLASS_ALIAS_FIELD = "$name = $value"
FIELD_DEFAULT_TEMPLATE = " = $default"
OPTIONAL_TEMPLATE = "typing.Optional[$type] = None"
UNION_TEMPLATE = "typing.Union[$type]"
LIST_TEMPLATE = "typing.List[$type]"
DICT_TEMPLATE = "typing.Dict[str, $type]"
FIXED_TEMPLATE = "types.Fixed = types.Fixed($properties)"
DATACLASS_FIELD = "dataclasses.field($properties)"
TYPE_TEMPLATE = 'typing.Type["$type"]'
DATE_TEMPLATE = "datetime.date($year, $month, $day)"
TIME_TEMPLATE = "datetime.time($hour, $minute, $second)"
TIME_MICROS_TEMPLATE = "datetime.time($hour, $minute, $second, $microsecond)"
DATETIME_TEMPLATE = "datetime.datetime($year, $month, $day, $hour, $minute, $second)"
DATETIME_MICROS_TEMPLATE = "datetime.datetime($year, $month, $day, $hour, $minute, $second, $microsecond)"
DECIMAL_TEMPLATE = "decimal.Decimal('$value')"
DECIMAL_TYPE_TEMPLATE = "types.Decimal($properties)"

ENUM_SYMBOL_TEMPLATE = "$key = $value"
ENUM_TEMPLATE = """

class $name(enum.Enum):
    $symbols
"""

CLASS_TEMPLATE = """
$decorator
class $name($base_class):
    $fields
"""

METACLASS_TEMPLATE = """
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
PYDANTIC_FIELD = "Field($properties)"
PYDANTIC_DECIMAL_TYPE_TEMPLATE = "condecimal(max_digits=$precision, decimal_places=$scale)"

field_template = Template(FIELD_TEMPLATE)
metaclass_field_template = Template(METACLASS_FIELD_TEMPLATE)
metaclass_alias_field_template = Template(METACLASS_ALIAS_FIELD)
field_default_template = Template(FIELD_DEFAULT_TEMPLATE)
optional_template = Template(OPTIONAL_TEMPLATE)
union_template = Template(UNION_TEMPLATE)
list_template = Template(LIST_TEMPLATE)
dict_template = Template(DICT_TEMPLATE)
fixed_template = Template(FIXED_TEMPLATE)
decimal_template = Template(DECIMAL_TEMPLATE)
decimal_type_template = Template(DECIMAL_TYPE_TEMPLATE)
pydantic_decimal_type_template = Template(PYDANTIC_DECIMAL_TYPE_TEMPLATE)
enum_symbol_template = Template(ENUM_SYMBOL_TEMPLATE)
enum_template = Template(ENUM_TEMPLATE)
dataclass_field_template = Template(DATACLASS_FIELD)
pydantic_field_template = Template(PYDANTIC_FIELD)
class_template = Template(CLASS_TEMPLATE)
metaclass_template = Template(METACLASS_TEMPLATE)
type_template = Template(TYPE_TEMPLATE)
date_template = Template(DATE_TEMPLATE)
time_template = Template(TIME_TEMPLATE)
time_micros_template = Template(TIME_MICROS_TEMPLATE)
datetime_template = Template(DATETIME_TEMPLATE)
datetime_micros_template = Template(DATETIME_MICROS_TEMPLATE)
imports_template = Template(IMPORTS_TEMPLATE.strip())
module_template = Template(MODULE_TEMPLATE.strip())
