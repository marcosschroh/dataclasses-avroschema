import enum
import typing
from dataclasses import dataclass, field
from string import Template

import fastavro
import stringcase

from dataclasses_avroschema import field_utils, serialization
from dataclasses_avroschema.types import JsonDict

from . import avro_to_python_utils, templates


class BaseClassEnum(str, enum.Enum):
    AVRO_MODEL = "AvroModel"
    PYDANTIC_MODEL = "BaseModel"
    AVRO_DANTIC_MODEL = "AvroBaseModel"


@dataclass
class ModelGenerator:
    base_class: str = BaseClassEnum.AVRO_MODEL.value
    field_identation: str = "\n    "
    imports: typing.Set[str] = field(default_factory=set)
    # extras is used fot extra code that is generated, for example Enums
    extras: typing.List[str] = field(default_factory=list)
    class_template: Template = templates.class_template
    dataclass_field_template: Template = templates.dataclass_field_template
    metadata_fields_mapper: typing.Dict[str, str] = field(
        default_factory=lambda: {
            "namespace": "namespace",
            "doc": "schema_doc",
            "alias": "aliases",
        }
    )
    matadata_field_templates: typing.Dict[str, Template] = field(
        default_factory=lambda: {
            "namespace": templates.metaclass_field_template,
            "doc": templates.metaclass_field_template,
            "alias": templates.metaclass_alias_field_template,
        }
    )
    base_class_to_imports: typing.Dict[str, str] = field(
        default_factory=lambda: {
            BaseClassEnum.AVRO_MODEL.value: "from dataclasses_avroschema import AvroModel",
            BaseClassEnum.PYDANTIC_MODEL.value: "from pydantic import BaseModel",
            BaseClassEnum.AVRO_DANTIC_MODEL.value: "from dataclasses_avroschema.avrodantic import AvroBaseModel",
        }
    )
    # represent the decorator to add in the base class
    base_class_decotator: str = ""

    def __post_init__(self) -> None:
        self.imports.add(self.base_class_to_imports[self.base_class])

        if self.base_class == BaseClassEnum.AVRO_MODEL.value:
            self.imports.add("import dataclasses")
            self.base_class_decotator = "@dataclasses.dataclass"
        else:
            self.dataclass_field_template = templates.pydantic_field_template

    @staticmethod
    def validate_schema(*, schema: JsonDict) -> None:
        """
        Validate that the schema is a valid avro schema
        """
        fastavro.parse_schema(schema)

    def render_imports(self) -> str:
        """
        Render the imports needed for the python classes.
        """
        # sort the imports
        list_imports = list(self.imports)
        list_imports.sort()

        imports = "\n".join([imp for imp in list_imports])
        return templates.imports_template.safe_substitute(imports=imports)

    def render_extras(self) -> str:
        return "".join([extra for extra in self.extras])

    def render_metaclass(self, *, schema: JsonDict) -> typing.Optional[str]:
        """
        Render Class Meta that contains the schema matadata
        """
        properties = self.field_identation.join(
            [
                self.matadata_field_templates[meta_avro_field].safe_substitute(
                    name=meta_field, value=schema.get(meta_avro_field)
                )
                for meta_avro_field, meta_field in self.metadata_fields_mapper.items()
                if schema.get(
                    meta_avro_field
                )  # TODO: replace this line with if (value := schema.get(meta_avro_field)) after drop py3.7
            ]
        )

        if properties:
            # some formating to remove identation at the end of the Class Meta to make it more compatible with black
            return (
                self.field_identation.join(
                    [line for line in templates.metaclass_template.safe_substitute(properties=properties).split("\n")]
                ).rstrip(self.field_identation)
                + "\n"
            )
        return None

    def render_class(self, *, schema: JsonDict) -> str:
        """
        Render the class generated from the schema
        """
        name: str = stringcase.pascalcase(schema["name"])
        record_fields: typing.List[JsonDict] = schema["fields"]

        # Sort the fields according whether it has a default value
        record_fields.sort(key=lambda field: 1 if "default" in field.keys() or field_utils.NULL in field["type"] else 0)

        rendered_fields = self.field_identation.join(
            [self.render_field(field=field, model_name=name) for field in record_fields]
        )

        rendered_class = templates.class_template.safe_substitute(
            name=name, decorator=self.base_class_decotator, base_class=self.base_class, fields=rendered_fields
        )

        class_metadata = self.render_metaclass(schema=schema)
        if class_metadata is not None:
            rendered_class += class_metadata

        return rendered_class

    def render_dataclass_field(self, properties: str) -> str:
        if self.base_class != BaseClassEnum.AVRO_MODEL.value:
            self.imports.add("from pydantic import Field")

        return self.dataclass_field_template.safe_substitute(properties=properties)

    def render(self, *, schema: JsonDict) -> str:
        """
        Render the module with the classes generated from the schema
        """
        return self.render_module(schemas=[schema])

    def render_module(self, *, schemas: typing.List[JsonDict]) -> str:
        """
        Render the module with the classes generated from the schemas
        """
        for schema in schemas:
            self.validate_schema(schema=schema)

        classes = "\n".join(self.render_class(schema=schema) for schema in schemas)
        imports = self.render_imports()
        extras = self.render_extras()

        return templates.module_template.safe_substitute(
            classes=classes,
            imports=imports,
            extras=extras,
        ).lstrip("\n")

    def render_field(self, field: JsonDict, model_name: str) -> str:
        """
        Render an avro field.

        1. If the field is a native one, we just render it.
        2. If the field is a record, array, map, fixed, enum
            we need to render the field again (recursive)
        3. If the field is a LogicalType, it may not have the
            the `name` property and the type is a `native` one
        """
        name = field.get("name", "")
        type = field["type"]
        default = field.get("default")

        # This flag tells whether the field is array, map, fixed
        is_complex_type = False

        if self.is_logical_type(field=field):
            is_complex_type = True
            # override the type so it can be use to get the default value in case that is needed
            type = field.get("logicalType") or field["type"]["logicalType"]
            language_type = self.parse_logical_type(field=field)

            if type == field_utils.DECIMAL:
                # set default to None because all the decimal has a default by design
                # and they are calculated in parse_decimal method
                default = None
        elif isinstance(type, dict):
            language_type = self.render_field(field=type, model_name=model_name)
        elif isinstance(type, list):
            language_type = self.parse_union(field_types=type, model_name=model_name)
        elif type == field_utils.ARRAY:
            is_complex_type = True
            language_type = self.parse_array(field=field, model_name=model_name)
        elif type == field_utils.MAP:
            is_complex_type = True
            language_type = self.parse_map(field=field, model_name=model_name)
        elif type == field_utils.ENUM:
            is_complex_type = True
            language_type = self.parse_enum(field=field)
        elif type == field_utils.FIXED:
            is_complex_type = True
            language_type = self.parse_fixed(field=field)
        elif type == field_utils.RECORD:
            record = f"\n{self.render_class(schema=field)}"
            is_complex_type = True
            self.extras.append(record)
            language_type = stringcase.pascalcase(field["name"])
        else:
            # Native field or Logical type using a native
            language_type = self.get_language_type(type=type)

        if is_complex_type:
            # If the field is a complext type, we need to return just the language_type
            result = language_type
        else:
            result = templates.field_template.safe_substitute(name=name, type=language_type)

        if default is not None:
            # optional field attribute
            default = self.get_field_default(field_type=type, default=field.get("default"), name=name)
            result += templates.field_default_template.safe_substitute(default=default)

        return result

    @staticmethod
    def is_logical_type(*, field: JsonDict) -> bool:
        if field.get("logicalType"):
            return True

        field_type = field["type"]
        return isinstance(field_type, dict) and field_type.get("logicalType") is not None

    def parse_logical_type(self, *, field: JsonDict) -> str:
        logical_type = field.get("logicalType") or field["type"]["logicalType"]

        # add the logical type import
        self.imports.add(avro_to_python_utils.LOGICAL_TYPES_IMPORTS[logical_type])
        field_name = field.get("name")

        if field_name is not None:
            field_repr = templates.field_template.safe_substitute(
                name=field_name, type=avro_to_python_utils.AVRO_TYPE_TO_PYTHON[logical_type]
            )

            if logical_type == field_utils.DECIMAL:
                # this is a special case for logical types
                default_decimal = self.parse_decimal(field=field)
                field_repr += templates.field_default_template.safe_substitute(default=default_decimal)

            return field_repr
        return avro_to_python_utils.AVRO_TYPE_TO_PYTHON[logical_type]

    def parse_decimal(self, *, field: JsonDict) -> str:
        schema: JsonDict = field["type"]
        precision = schema["precision"]
        scale = schema["scale"]
        properties = f"scale={scale}, precision={precision}"
        default = field.get("default")

        if self.base_class == BaseClassEnum.AVRO_MODEL.value:
            self.imports.add("from dataclasses_avroschema import types")

            if default is not None:
                default = templates.decimal_template.safe_substitute(
                    value=serialization.string_to_decimal(value=default, schema=schema)
                )
                properties += f", default={default}"
            return templates.decimal_type_template.safe_substitute(properties=properties)
        else:
            # we should render a pydantic condecimal
            self.imports.add("from pydantic import condecimal")
            return templates.pydantic_decimal_type_template.safe_substitute(scale=scale, precision=precision)

    def parse_union(self, *, field_types: typing.List, model_name: str) -> str:
        """
        Parse an Avro union

        An union field is an array like ["null", "str", "int", ...]

        If the first element is `null` it means that the property is optional.
        The first item is the actual type of the field a AVRO specifies.

        Attributes:
            field_types: List of avro types
            model_name: name of the model that contains the `union`
        """
        first_type = field_types[0]

        if first_type == field_utils.NULL:
            # It is an optional field, we should include in the imports typing
            # an use the optional Template
            self.imports.add("import typing")

            # the union can have native types or custom types
            # if the type is not in the AVRO_TYPE_TO_PYTHON it means that it is a CustomType
            if len(field_types) > 2:
                language_types = self.parse_union(field_types=field_types[1:], model_name=model_name)
            elif isinstance(field_types[1], dict):
                # TODO: check what happens with more than 2 complex types
                language_types = self.render_field(field=field_types[1], model_name=model_name)
            else:
                language_types = ", ".join(
                    # TODO: check default, seems doing nothing
                    [self.get_language_type(type=type, default=type, model_name=model_name) for type in field_types[1:]]
                )

            return templates.optional_template.safe_substitute(type=language_types)
        else:
            # It is a field that does not contain `null`
            # unions like ["string", "null"] don't make sense for the language as
            # the default value should be `string`, `null` is not possible as default

            # remove all the `null` apparences
            field_types = [field for field in field_types if field != field_utils.NULL]

            if len(field_types) >= 2:
                # an union with more than 2 types
                self.imports.add("import typing")

                language_types_list = []
                for type in field_types:
                    if isinstance(type, dict):
                        # it is a complex type like array, dict, enum, fixed or record
                        # it needs to be render
                        language_types_list.append(self.render_field(field=type, model_name=model_name))
                    else:
                        language_types_list.append(self.get_language_type(type=type, default=type))

                language_types_repr = ", ".join(
                    [self.get_language_type(type=type, default=type) for type in language_types_list]
                )
                return templates.union_template.safe_substitute(type=language_types_repr)
            else:
                # If for some reason `null` was inluded we should ignore it
                # the union has 2 types, so we return the first language type
                # example: "types": ["string", "null"]
                return self.get_language_type(type=first_type)

    def parse_array(self, field: JsonDict, model_name: str) -> str:
        """
        Parse an Avro array

        The type is is specify in the `items` attribute

        Example:
            {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}
        """
        type = field["items"]
        language_type = self._get_complex_langauge_type(type=type, model_name=model_name)

        return templates.list_template.safe_substitute(type=language_type)

    def parse_map(self, field: JsonDict, model_name: str) -> str:
        """
        Parse an Avro map

        The type is is specify in the `values` attribute. All the keys must be `string`

        Example:
            {"name": "accounts_money", "type": {"type": "map", "values": "float", "name": "accounts_money"}},
        """
        type = field["values"]
        language_type = self._get_complex_langauge_type(type=type, model_name=model_name)

        return templates.dict_template.safe_substitute(type=language_type)

    def parse_fixed(self, field: JsonDict) -> str:
        self.imports.add("from dataclasses_avroschema import types")
        properties = f"{field['size']}"

        namespace = field.get("namespace")
        aliases = field.get("aliases")

        if namespace is not None:
            properties += f', namespace="{namespace}"'

        if aliases is not None:
            properties += f", aliases={aliases}"

        return templates.fixed_template.safe_substitute(properties=properties)

    def parse_enum(self, field: JsonDict) -> str:
        """
        Parse an Avro Enum

        Avro Enums are asociated with enum.Enum types in python.
        We need a template for it in order to create the Enum
        """
        self.imports.add("import enum")

        field_name: str = field["name"]
        enum_name = stringcase.pascalcase(field_name)
        symbols = self.field_identation.join(
            [
                templates.enum_symbol_template.safe_substitute(key=stringcase.uppercase(symbol), value=f'"{symbol}"')
                for symbol in field["symbols"]
            ]
        )

        enum_class = templates.enum_template.safe_substitute(name=enum_name, symbols=symbols)
        self.extras.append(enum_class)

        return enum_name

    def _get_complex_langauge_type(self, *, type: typing.Any, model_name: str) -> str:
        """
        Get the language type for complext types (array and maps)
        """
        self.imports.add("import typing")

        if isinstance(type, dict):
            language_type = self.render_field(field=type, model_name=model_name)
        elif isinstance(type, list):
            language_type = self.parse_union(field_types=type, model_name=model_name)
        else:
            language_type = self.get_language_type(type=type, model_name=model_name)

        return language_type

    def get_language_type(
        self, *, type: str, default: typing.Optional[str] = None, model_name: typing.Optional[str] = None
    ) -> str:
        if type in (field_utils.FIXED, field_utils.INT, field_utils.FLOAT):
            self.imports.add("from dataclasses_avroschema import types")

        if type == model_name:
            # it means that it is a one-to-self-relationship
            return templates.type_template.safe_substitute(type=type)

        if default is not None:
            return str(avro_to_python_utils.AVRO_TYPE_TO_PYTHON.get(type, default))
        return str(avro_to_python_utils.AVRO_TYPE_TO_PYTHON.get(type, type))

    def get_field_default(self, *, field_type: str, default: typing.Any, name: str) -> typing.Any:
        """
        Returns the default value according to the field type

        TODO: docstrings

        Example:
            If the default is "bond" the method should return '\n"bond\n"' so the double quotes
            won't be scaped during the field render
        """
        if field_type in (field_utils.STRING, field_utils.UUID):
            return f'"{default}"'
        elif field_type == field_utils.BYTES:
            return f'b"{default}"'
        elif isinstance(field_type, dict) and field_type.get("type") == field_utils.ENUM:
            return f"{stringcase.pascalcase(name)}.{stringcase.uppercase(default)}"
        elif isinstance(
            default,
            (
                list,
                dict,
            ),
        ):
            if default:
                # it is an array or maps with some defaults that we should
                # express with a lambda function
                properties = f"default_factory=lambda: {default}"
            else:
                # it is an array or maps with `[]` or `{} ` as default
                properties = f"default_factory={default.__class__.__name__}"
            return self.render_dataclass_field(properties=properties)
        elif isinstance(field_type, list):
            return self.get_field_default(field_type=field_type[0], default=default, name=name)
        elif field_type in avro_to_python_utils.LOGICAL_TYPES_TO_PYTHON:
            func = avro_to_python_utils.LOGICAL_TYPES_TO_PYTHON[field_type]
            python_type = func(default)
            template_func = avro_to_python_utils.LOGICAL_TYPE_TEMPLATES[field_type]
            return template_func(python_type)
        else:
            return default
