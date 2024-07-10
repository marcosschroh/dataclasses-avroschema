import copy
import dataclasses
import json
import typing
from dataclasses import dataclass, field
from string import Template

import casefy

from dataclasses_avroschema import serialization
from dataclasses_avroschema.fields import field_utils
from dataclasses_avroschema.types import AvroTypeRepr, JsonDict

from . import (
    avro_to_python_utils,
    templates,
)


class FieldRepresentation(typing.NamedTuple):
    name: str
    string_representation: str
    has_default: bool


@dataclass
class BaseGenerator:
    field_identation: str = "\n    "
    imports: typing.Set[str] = field(default_factory=set)
    imports_dict: typing.Dict[str, str] = field(default_factory=dict)

    # extras is used fot extra code that is generated, for example Enums
    extras: typing.List[str] = field(default_factory=list)

    metadata_fields_mapper: typing.Dict[str, str] = field(
        default_factory=lambda: {
            # doc is not included because it is rendered as docstrings
            "namespace": "namespace",
            "aliases": "aliases",
        }
    )
    metadata_field_templates: typing.Dict[str, Template] = field(
        default_factory=lambda: {
            "namespace": templates.metaclass_field_template,
            "doc": templates.metaclass_field_template,
            "aliases": templates.metaclass_alias_field_template,
            "original_schema": templates.metaclass_schema_field_template,
        }
    )
    # represent the decorator to add in the base class
    base_class_decorator: str = ""
    base_class: str = field(init=False)
    field_template: Template = field(init=False)
    avro_type_to_lang: typing.Dict[str, str] = field(init=False)
    logical_types_imports: typing.Dict[str, str] = field(init=False)

    # Boolean to indicate whether original_schema field containing the original schema string should be generated in
    # Meta class of all generated objects
    include_original_schema: bool = False

    def __post_init__(self) -> None:
        self.avro_type_to_lang = avro_to_python_utils.AVRO_TYPE_TO_PYTHON
        self.logical_types_imports = avro_to_python_utils.LOGICAL_TYPES_IMPORTS

    def render(self, schemas: typing.List[JsonDict]) -> str:
        classes = "\n".join(self.render_class(schema=schema) for schema in schemas)
        imports = self.render_imports()
        extras = self.render_extras()

        return templates.module_template.safe_substitute(
            classes=classes,
            imports=imports,
            extras=extras,
        ).lstrip("\n")

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

    def render_metaclass(
        self, *, schema: JsonDict, field_order: typing.Optional[typing.List[str]] = None, decorator: str = ""
    ) -> typing.Optional[str]:
        """
        Render Class Meta that contains the schema matadata
        """
        metadata = [
            self.metadata_field_templates[meta_avro_field].safe_substitute(name=meta_field, value=value)
            for meta_avro_field, meta_field in self.metadata_fields_mapper.items()
            if (value := schema.get(meta_avro_field))
        ]

        # Parse the entire schema string into the Meta class field "original_schema" for each class.
        # If self.include_original_schema is set to True.
        if self.include_original_schema:
            metadata.append(self._add_schema_to_metaclass(self.metadata_field_templates["original_schema"], schema))

        if field_order is not None:
            metadata.append(
                templates.metaclass_alias_field_template.safe_substitute(
                    name="field_order",
                    value=field_order,
                )
            )

        properties = self.field_identation.join(metadata)

        if properties:
            # some formating to remove identation at the end of the Class Meta to make it more compatible with black
            return self.field_identation.join(
                [
                    line
                    for line in templates.metaclass_template.safe_substitute(
                        properties=properties, decorator=decorator
                    ).split("\n")
                ]
            ).rstrip(self.field_identation)
        return None

    def render_docstring(self, *, docstring: typing.Optional[str]) -> str:
        """
        Render the module with the classes generated from the schema
        """
        if not docstring:
            return ""

        indented = self.field_identation + self.field_identation.join(docstring.splitlines())

        return f'{self.field_identation}"""{indented}{self.field_identation}"""'

    def render_class(self, *, schema: JsonDict) -> str:
        """
        Render the class generated from the schema
        """
        name: str = casefy.pascalcase(schema["name"])
        record_fields: typing.List[JsonDict] = schema["fields"]

        # Sort the fields according whether it has a default value
        fields_representation: typing.List[FieldRepresentation] = [
            self.render_field(field=field, model_name=name) for field in record_fields
        ]

        fields_representation_copy = copy.deepcopy(fields_representation)
        fields_representation.sort(key=lambda field: 1 if field.has_default else 0)

        field_order = None
        if fields_representation_copy != fields_representation:
            field_order = [field.name for field in fields_representation_copy]

        rendered_fields_string = self.field_identation.join(
            field.string_representation for field in fields_representation
        )
        docstring = self.render_docstring(docstring=schema.get("doc"))

        rendered_class = templates.class_template.safe_substitute(
            name=name,
            decorator=self.base_class_decorator,
            base_class=self.base_class,
            fields=rendered_fields_string,
            docstring=docstring,
        )

        class_metadata = self.render_metaclass(schema=schema, field_order=field_order)
        if class_metadata is not None:
            rendered_class += class_metadata

        return rendered_class

    def render_dataclass_field(self, properties: str) -> str:
        return self.field_template.safe_substitute(properties=properties)

    def render_field(self, field: JsonDict, model_name: str) -> FieldRepresentation:
        """
        Render an avro field.

        1. If the field is a native one, we just render it.
        2. If the field is a record, array, map, fixed, enum
            we need to render the field again (recursive)
        3. If the field is a LogicalType, it may not have the
            the `name` property and the type is a `native` one
        """
        name = self.generate_field_name(field)

        type: AvroTypeRepr = field["type"]
        default = field.get("default", dataclasses.MISSING)
        field_metadata = self.get_field_metadata(field)

        # This flag tells whether the field is array, map, fixed
        is_complex_type = has_default = False

        if self.is_logical_type(field=field):
            is_complex_type = True
            # override the type so it can be use to get the default value in case that is needed
            type = field.get("logicalType") or field["type"]["logicalType"]
            language_type = self.parse_logical_type(field=field)
        elif isinstance(type, dict):
            field_representation = self.render_field(field=type, model_name=model_name)
            language_type = field_representation.string_representation
            has_default = field_representation.has_default
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
            language_type = casefy.pascalcase(field["name"])
        else:
            # Native field
            language_type = self.get_language_type(type=type, model_name=model_name)

            # check if the language type must be replaced with some extra class
            # specified in the field metadata only after the native type was resolved
            type_from_metadata = self._resolve_type_from_metadata(field=field)
            language_type = type_from_metadata or language_type

        if is_complex_type or not name:
            # If the field is a complext type or
            # name is an empty string (it means that the type is a native type
            # with the form {"type": "a_primitive_type"}, example {"type": "string"})
            result = language_type
        else:
            result = templates.field_type_template.safe_substitute(name=name, type=language_type)

        # optional field attribute
        default_generated = self.get_field_default(
            field_type=type, default=default, name=name, field_metadata=field_metadata
        )

        if default_generated not in (
            dataclasses.MISSING,
            "",
        ):
            if type != field_utils.DECIMAL:
                result += templates.field_default_template.safe_substitute(default=default_generated)
            if default is not dataclasses.MISSING:
                has_default = True

        return FieldRepresentation(name=name, string_representation=result, has_default=has_default)

    @staticmethod
    def generate_field_name(field: JsonDict) -> str:
        field_name = field.get("name", "")

        if field_name and not field_name.isidentifier():
            valid_identifier = casefy.snakecase(field_name)
            if valid_identifier != field_name:
                aliases = field.get("aliases", [])

                if valid_identifier not in aliases:
                    aliases.append(field_name)
                    field["aliases"] = aliases

            return valid_identifier
        return field_name

    @staticmethod
    def is_logical_type(*, field: JsonDict) -> bool:
        if field.get("logicalType"):
            return True

        field_type = field["type"]
        return isinstance(field_type, dict) and field_type.get("logicalType") is not None

    def parse_logical_type(self, *, field: JsonDict) -> str:
        field_name = field.get("name")
        default = field.get("default")
        field = field if field_name is None else field["type"]
        logical_type = field["logicalType"]

        type_from_metadata = self._resolve_type_from_metadata(field=field)

        if type_from_metadata is not None:
            type = type_from_metadata
        elif logical_type == field_utils.DECIMAL:
            # this is a special case for logical types
            type = self.parse_decimal(field=field, default=default)
        else:
            # add the logical type import
            self.imports.add(self.logical_types_imports[logical_type])
            type = self.avro_type_to_lang[logical_type]

        if field_name is not None:
            field_repr = templates.field_type_template.safe_substitute(name=field_name, type=type)
            return field_repr

        return type

    def parse_decimal(self, *, field: JsonDict, default: typing.Optional[str] = None) -> str:
        precision = field["precision"]
        scale = field["scale"]

        self.imports.add("from dataclasses_avroschema import types")
        field_repr = templates.decimal_type_template.safe_substitute(precision=precision, scale=scale)

        if default is not None:
            self.imports.add("import decimal")
            default = templates.decimal_template.safe_substitute(
                value=serialization.string_to_decimal(value=default, schema=field)
            )
            field_repr += templates.field_default_template.safe_substitute(default=default)
        return field_repr

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

        # XXX: Maybe more useful in general
        def render_type(typ: str) -> str:
            if isinstance(typ, dict):
                field_representation = self.render_field(field=typ, model_name=model_name)
                return field_representation.string_representation
            else:
                return self.get_language_type(type=typ, model_name=model_name)

        if field_utils.NULL in field_types and len(field_types) == 2:
            # It is an optional field, we should include in the imports typing
            # and use the optional Template
            self.imports.add("import typing")
            (field_type,) = [f for f in field_types if f != field_utils.NULL]
            language_types = render_type(field_type)
            return templates.optional_template.safe_substitute(type=language_types)
        elif len(field_types) >= 2:
            # a union with more than 2 types
            self.imports.add("import typing")
            language_types_repr = ", ".join(render_type(t) for t in field_types)
            return templates.union_template.safe_substitute(type=language_types_repr)
        else:
            return render_type(field_types[0])

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
        properties = f"size={field['size']}"

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

        enum_name: str = field["name"]

        symbols_map = {}
        symbols: typing.List[str] = field["symbols"]
        for symbol in symbols:
            key = casefy.uppercase(symbol)
            if key in symbols:
                key = symbol
            symbols_map[key] = symbol

        symbols_repr = self.field_identation.join(
            [
                templates.enum_symbol_template.safe_substitute(key=key, value=f'"{value}"')
                for key, value in symbols_map.items()
            ]
        )

        docstring = self.render_docstring(docstring=field.get("doc"))
        enum_class = templates.enum_template.safe_substitute(name=enum_name, symbols=symbols_repr, docstring=docstring)
        metaclass = self.render_metaclass(schema=field, decorator=templates.METACLASS_DECORATOR)

        if metaclass:
            enum_class += metaclass

        self.extras.append(enum_class)

        return enum_name

    def _get_complex_langauge_type(self, *, type: typing.Any, model_name: str) -> str:
        """
        Get the language type for complex types (array and maps)
        """
        self.imports.add("import typing")

        if isinstance(type, dict):
            field_representation = self.render_field(field=type, model_name=model_name)
            language_type = field_representation.string_representation
        elif isinstance(type, list):
            language_type = self.parse_union(field_types=type, model_name=model_name)
        else:
            language_type = self.get_language_type(type=type, model_name=model_name)

        return language_type

    def get_language_type(
        self,
        *,
        type: str,
        default: typing.Optional[str] = None,
        model_name: typing.Optional[str] = None,
    ) -> str:
        if type in (field_utils.INT, field_utils.FLOAT):
            self.imports.add("from dataclasses_avroschema import types")

        if type == model_name:
            # it means that it is a one-to-self-relationship
            return templates.type_template.safe_substitute(type=type)
        elif type not in self.avro_type_to_lang:
            # it means the type points to the an already specified type so it contains the type name
            # with optional namespaces, e.g. my_namespace.users.User
            # In this case we should return the last part of the string
            return type.split(".")[-1]
        elif default is not None:
            return str(self.avro_type_to_lang.get(type, default))
        else:
            return str(self.avro_type_to_lang.get(type, type))

    def get_field_metadata(self, field: JsonDict) -> JsonDict:
        keys_to_ignore = [
            "name",
            "type",
            "default",
            "pydantic-class",
        ]

        type = field["type"]

        if type == field_utils.ARRAY:
            keys_to_ignore.append("items")
        elif type == field_utils.MAP:
            keys_to_ignore.append("values")
        elif type == field_utils.FIXED:
            keys_to_ignore.extend(["namespace", "aliases", "size"])
        elif type == field_utils.ENUM:
            keys_to_ignore.extend(["symbols", "namespace", "aliases", "doc"])
        elif type == field_utils.RECORD:
            keys_to_ignore.extend(["fields", "doc", "aliases", "namespace"])
        elif self.is_logical_type(field=field):
            keys_to_ignore.extend(
                [
                    "logicalType",
                ]
            )

        return {name: value for name, value in field.items() if name not in keys_to_ignore}

    def _resolve_type_from_metadata(self, *, field: JsonDict) -> typing.Optional[str]:
        return None

    def get_field_default(
        self,
        *,
        field_type: AvroTypeRepr,
        default: typing.Any,
        name: str,
        field_metadata: typing.Optional[JsonDict] = None,
    ) -> typing.Any:
        """
        Returns the default value according to the field type

        TODO: docstrings

        Example:
            If the default is "bond" the method should return '"bond"' so the double quotes
            won't be scaped during the field render
        """
        field_metadata = field_metadata or {}
        field_metadata_repr = None
        default_repr = ""

        if isinstance(field_type, dict):
            inner_type = field_type["type"]
            inner_name = field_type.get("name", "")

            # Check that internal field name is different to the original name
            # for example: {"name": "age", "type": { "type": "array", "items": "string", "name": "my_age" }}
            # in this case my_age is not in age which means that this must be reflected in the model
            # This does not applu to `enums` and `records`
            if inner_name not in name and inner_type not in (
                field_utils.ENUM,
                field_utils.RECORD,
            ):
                field_metadata["inner_name"] = inner_name

            inner_default_repr = self.get_field_default(field_type=inner_type, name=inner_name or name, default=default)

            if inner_default_repr not in (None, dataclasses.MISSING):
                default_repr += inner_default_repr
        elif default is dataclasses.MISSING:
            pass
        elif field_type in (
            field_utils.STRING,
            field_utils.UUID,
        ):
            default_repr = f'"{default}"'
        elif field_type in (
            field_utils.BYTES,
            field_utils.FIXED,
        ):
            default_repr = f'b"{default}"'
        elif field_type == field_utils.ENUM:
            default_repr = f"{name}.{casefy.uppercase(default)}"
        elif isinstance(field_type, list):
            # union type
            default_repr = self.get_field_default(field_type=field_type[0], default=default, name=name)
        elif isinstance(default, (dict, list)):
            # Then is can be a regular dict as default or a record
            if default:
                if field_type not in field_utils.AVRO_TYPES:
                    # Try to get the last part in case that the type is namespaced `types.bus_type.Bus`
                    field_type = field_type.split(".")[-1]
                    default = templates.instance_template.safe_substitute(type=field_type, properties=f"**{default}")

                return f"{default}"
            return default.__class__.__name__
        elif field_type in avro_to_python_utils.LOGICAL_TYPES_TO_PYTHON:
            func = avro_to_python_utils.LOGICAL_TYPES_TO_PYTHON[field_type]
            python_type = func(default)
            template_func = avro_to_python_utils.LOGICAL_TYPE_TEMPLATES[field_type]
            default_repr = template_func(python_type)
        else:
            default_repr = str(default)

        dataclass_field_properties = []
        if field_metadata:
            field_metadata_repr = f"metadata={field_metadata}"

        if field_metadata_repr or isinstance(default, (dict, list)):
            dataclass_field_properties = [field_metadata_repr]

            if isinstance(default, (dict, list)):
                if default:
                    dataclass_prop = f"default_factory=lambda: {default_repr}"
                else:
                    dataclass_prop = f"default_factory={default_repr}"

                dataclass_field_properties.append(dataclass_prop)
            else:
                if default is not dataclasses.MISSING:
                    dataclass_field_properties.append(f"default={default_repr}")

            default_repr = self.render_dataclass_field(
                properties=", ".join([prop for prop in dataclass_field_properties if prop])
            )

        return default_repr

    @staticmethod
    def _add_schema_to_metaclass(schema_template: Template, schema: JsonDict) -> str:
        """
        Parses provided schema to ModelGenerator.render() to a Meta field string by using
        metaclass_schema_field_template.
        """
        return schema_template.safe_substitute(name="original_schema", schema=json.dumps(schema))
