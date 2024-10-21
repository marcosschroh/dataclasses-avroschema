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


@dataclasses.dataclass
class FieldRepresentation:
    name: str
    avro_type: typing.Any
    type_hint: str
    default: typing.Any
    template: Template
    metadata: JsonDict = dataclasses.field(default_factory=dict)
    children: typing.List["FieldRepresentation"] = dataclasses.field(default_factory=list)
    inner_name: str = ""

    def __post_init__(self) -> None:
        if isinstance(self.avro_type, list):
            self.avro_type = self.avro_type[0]

        if isinstance(self.avro_type, dict):
            inner_type = self.avro_type["type"]
            self.inner_name = self.avro_type.get("name", "")

            if self.children:
                self.child_field = self.children[0]
                self.avro_type = self.child_field.avro_type
                self.type_hint = self.type_hint or self.child_field.type_hint
                self.default = self.default if self.default is not dataclasses.MISSING else self.child_field.default

            # Check that internal field name is different to the original name
            # for example: {"name": "age", "type": { "type": "array", "items": "string", "name": "my_age" }}
            # in this case my_age is not in age which means that this must be reflected in the model
            # This does not applu to `enums` and `records`
            if self.inner_name not in self.name and inner_type not in (
                field_utils.ENUM,
                field_utils.RECORD,
            ):
                self.metadata["inner_name"] = self.inner_name

        # update all metadata based on all children
        for child in self.children:
            self.metadata.update(child.metadata)

    def to_string(self) -> str:
        """
        Convert a field to string
        """
        result = templates.field_type_template.safe_substitute(name=self.name, type=self.type_hint)

        # optional field attribute
        default_generated = self.get_field_default()

        if (
            default_generated
            not in (
                dataclasses.MISSING,
                "",
            )
            and self.avro_type != field_utils.DECIMAL
        ):
            result += templates.field_default_template.safe_substitute(default=default_generated)

        return result

    def get_field_default(self) -> str:
        """
        Returns the default value according to the field type

        TODO: docstrings

        Example:
            If the default is "bond" the method should return '"bond"' so the double quotes
            won't be scaped during the field render
        """
        field_metadata = self.metadata or {}
        field_metadata_repr = None
        default_repr = ""

        if self.default is dataclasses.MISSING:
            ...
        elif self.avro_type in (
            field_utils.STRING,
            field_utils.UUID,
        ):
            default_repr = f'"{self.default}"'
        elif self.avro_type in (
            field_utils.BYTES,
            field_utils.FIXED,
        ):
            default_repr = f'b"{self.default}"'
        elif self.avro_type == field_utils.ENUM:
            enum_name = self.inner_name or self.type_hint
            default_repr = f"{casefy.pascalcase(enum_name)}.{casefy.uppercase(self.default)}"
        elif isinstance(self.default, (dict, list)):
            # Then is can be a regular dict as default or a record
            if self.default:
                if self.avro_type not in field_utils.AVRO_TYPES:
                    # Try to get the last part in case that the type is namespaced `types.bus_type.Bus`
                    field_type = self.avro_type.split(".")[-1]
                    default_repr = templates.instance_template.safe_substitute(
                        type=field_type, properties=f"**{self.default}"
                    )
                else:
                    default_repr = str(self.default)
            else:
                default_repr = self.default.__class__.__name__
        elif self.avro_type in avro_to_python_utils.LOGICAL_TYPES_TO_PYTHON:
            func = avro_to_python_utils.LOGICAL_TYPES_TO_PYTHON[self.avro_type]
            python_type = func(self.default)
            template_func = avro_to_python_utils.LOGICAL_TYPE_TEMPLATES[self.avro_type]
            default_repr = template_func(python_type)
        else:
            default_repr = str(self.default)

        dataclass_field_properties = []
        if field_metadata:
            field_metadata_repr = f"metadata={field_metadata}"

        if field_metadata_repr or isinstance(self.default, (dict, list)):
            dataclass_field_properties = [field_metadata_repr]

            if isinstance(self.default, (dict, list)):
                if self.default:
                    dataclass_prop = f"default_factory=lambda: {default_repr}"
                else:
                    dataclass_prop = f"default_factory={default_repr}"

                dataclass_field_properties.append(dataclass_prop)
            else:
                if self.default is not dataclasses.MISSING:
                    dataclass_field_properties.append(f"default={default_repr}")

            default_repr = self.render_dataclass_field(
                properties=", ".join([prop for prop in dataclass_field_properties if prop])
            )

        return default_repr

    def render_dataclass_field(self, properties: str) -> str:
        return self.template.safe_substitute(properties=properties)


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
            "default": "default",
        }
    )
    metadata_field_templates: typing.Dict[str, Template] = field(
        default_factory=lambda: {
            "namespace": templates.metaclass_field_template,
            "doc": templates.metaclass_field_template,
            "aliases": templates.metaclass_alias_field_template,
            "original_schema": templates.metaclass_schema_field_template,
            "default": templates.metaclass_field_template,
            "schema_name": templates.metaclass_field_template,
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

    def add_class_imports(self) -> None: ...

    def _resolve_type_from_metadata(self, *, field: JsonDict) -> typing.Optional[str]: ...

    def render(self, schemas: typing.List[JsonDict]) -> str:
        result = []

        for schema in schemas:
            if "fields" in schema:
                result.append(self.render_class(schema=schema))
            else:
                # If is not a Record then it is an Enum
                self.render_field(field=schema, model_name="", parent_field_name=schema["name"])

        classes = "\n".join(result)
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
        self,
        *,
        schema: JsonDict,
        field_order: typing.Optional[typing.List[str]] = None,
        decorator: str = "",
        add_schema_name: bool = False,
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

        if add_schema_name:
            metadata.append(
                self.metadata_field_templates["schema_name"].safe_substitute(name="schema_name", value=schema["name"])
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

    def render_class(self, *, schema: JsonDict, parent_field_name: typing.Optional[str] = None) -> str:
        """
        Render the class generated from the schema
        """
        model_name: str = casefy.pascalcase(schema["name"])

        record_fields: typing.List[JsonDict] = schema["fields"]
        self.add_class_imports()

        # Sort the fields according whether it has a default value
        fields_representation: typing.List[FieldRepresentation] = [
            self.render_field(field=field, model_name=model_name, parent_field_name=parent_field_name or field["name"])
            for field in record_fields
        ]

        fields_representation_copy = copy.copy(fields_representation)
        fields_representation.sort(key=lambda field: field.default is not dataclasses.MISSING)

        field_order = None
        if fields_representation_copy != fields_representation:
            field_order = [field.name for field in fields_representation_copy]

        rendered_fields_string = self.field_identation.join(field.to_string() for field in fields_representation)
        docstring = self.render_docstring(docstring=schema.get("doc"))

        rendered_class = templates.class_template.safe_substitute(
            name=model_name,
            decorator=self.base_class_decorator,
            base_class=self.base_class,
            fields=rendered_fields_string,
            docstring=docstring,
        )

        add_schema_name = model_name != schema["name"]
        class_metadata = self.render_metaclass(schema=schema, field_order=field_order, add_schema_name=add_schema_name)
        if class_metadata is not None:
            rendered_class += class_metadata

        return rendered_class

    def render_field(self, field: JsonDict, model_name: str, parent_field_name: str) -> FieldRepresentation:
        """
        Render an avro field.

        1. If the field is a native one, we just render it.
        2. If the field is a record, array, map, fixed, enum
            we need to render the field again (recursive)
        3. If the field is a LogicalType, it may not have the
            the `name` property and the type is a `native` one
        """
        name = self.generate_field_name(field)

        avro_type: AvroTypeRepr = field["type"]
        default = field.get("default", dataclasses.MISSING)
        field_metadata = self.get_field_metadata(field)
        children = None

        if self.is_logical_type(field=field):
            # override the type so it can be use to get the default value in case that is needed
            avro_type = field.get("logicalType") or field["type"]["logicalType"]
            type_hint = self.parse_logical_type(field=field)
        elif isinstance(avro_type, dict):
            type_hint = ""
            children = [self.render_field(field=avro_type, model_name=model_name, parent_field_name=name)]
        elif isinstance(avro_type, list):
            type_hint, children = self.parse_union(field_types=avro_type, model_name=model_name, parent_field_name=name)
        elif avro_type == field_utils.ARRAY:
            type_hint, children = self.parse_array(field=field, model_name=model_name, parent_field_name=name)
        elif avro_type == field_utils.MAP:
            type_hint, children = self.parse_map(field=field, model_name=model_name, parent_field_name=name)
        elif avro_type == field_utils.ENUM:
            type_hint = self.parse_enum(field=field)
            # We must set the default Enums type level default to dataclasses.MISSING
            # as it is set in the Meta class.
            # Check https://github.com/marcosschroh/dataclasses-avroschema/issues/665
            default = dataclasses.MISSING
        elif avro_type == field_utils.FIXED:
            type_hint = self.parse_fixed(field=field)
        elif avro_type == field_utils.RECORD:
            type_hint = casefy.pascalcase(name)

            record = f"\n{self.render_class(schema=field, parent_field_name=name)}"
            self.extras.append(record)

            if parent_field_name == type_hint:
                type_hint = f"_{name}"
                clashed_class = (
                    f"\n{templates.metaclass_alias_field_template.safe_substitute(name=type_hint, value=name)}"
                )
                self.extras.append(clashed_class)
        else:
            # Native field
            type_hint = self.get_language_type(avro_type=avro_type, field_name=name, model_name=model_name)

            # check if the language type must be replaced with some extra class
            # specified in the field metadata only after the native type was resolved
            type_from_metadata = self._resolve_type_from_metadata(field=field)
            type_hint = type_from_metadata or type_hint

        return FieldRepresentation(
            name=name,
            avro_type=avro_type,
            type_hint=type_hint,
            template=self.field_template,
            default=default,
            metadata=field_metadata,
            children=children or [],
        )

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
        field = field if field_name is None or field.get("logicalType") else field["type"]
        logical_type = field["logicalType"]

        type_from_metadata = self._resolve_type_from_metadata(field=field)

        if type_from_metadata is not None:
            type_hint = type_from_metadata
        elif logical_type == field_utils.DECIMAL:
            # this is a special case for logical types
            type_hint = self.parse_decimal(field=field, default=default)
        elif logical_type not in self.logical_types_imports:
            # Then it is a custom logicalType, so we default to the native type
            type_hint = self.get_language_type(avro_type=field["type"])
        else:
            # add the logical type import
            self.imports.add(self.logical_types_imports[logical_type])
            type_hint = self.avro_type_to_lang[logical_type]

        return type_hint

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

    def parse_union(
        self, *, field_types: typing.List, model_name: str, parent_field_name: str
    ) -> typing.Tuple[str, typing.List[FieldRepresentation]]:
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
        def render_type(avro_type: typing.Union[str, dict]) -> FieldRepresentation:
            avro_type = self.type_to_defined_types(avro_type)

            return self.render_field(field=avro_type, model_name=model_name, parent_field_name=parent_field_name)

        if field_utils.NULL in field_types and len(field_types) == 2:
            # It is an optional field, we should include in the imports typing
            # and use the optional Template
            self.imports.add("import typing")
            field_type = [f for f in field_types if f != field_utils.NULL]
            field_representation = render_type(field_type[0])
            type_hint = templates.optional_template.safe_substitute(type=field_representation.type_hint)
            return type_hint, [field_representation]
        elif len(field_types) >= 2:
            # a union with more than 2 types
            self.imports.add("import typing")
            children = [render_type(t) for t in field_types]
            language_types_repr = ", ".join(child.type_hint for child in children)
            type_hint = templates.union_template.safe_substitute(type=language_types_repr)
            return type_hint, children
        else:
            # This is a weird definitions when an union can have only one type
            #  {"name": "money_available", "type": ["double"]},
            field_representation = render_type(field_types[0])
            return field_representation.type_hint, [field_representation]

    def parse_array(
        self, field: JsonDict, model_name: str, parent_field_name: str
    ) -> typing.Tuple[str, typing.List[FieldRepresentation]]:
        """
        Parse an Avro array

        The type is is specify in the `items` attribute

        Example:
            {"name": "pets", "type": {"type": "array", "items": "string", "name": "pet"}}
        """
        self.imports.add("import typing")
        avro_type = self.type_to_defined_types(field["items"])

        field_representation = self.render_field(
            field=avro_type, model_name=model_name, parent_field_name=parent_field_name
        )
        type_hint = templates.list_template.safe_substitute(type=field_representation.type_hint)

        return type_hint, [field_representation]

    def parse_map(
        self, field: JsonDict, model_name: str, parent_field_name: str
    ) -> typing.Tuple[str, typing.List[FieldRepresentation]]:
        """
        Parse an Avro map

        The type is is specify in the `values` attribute. All the keys must be `string`

        Example:
            {"name": "accounts_money", "type": {"type": "map", "values": "float", "name": "accounts_money"}},
        """
        self.imports.add("import typing")
        avro_type = self.type_to_defined_types(field["values"])

        field_representation = self.render_field(
            field=avro_type, model_name=model_name, parent_field_name=parent_field_name
        )
        type_hint = templates.dict_template.safe_substitute(type=field_representation.type_hint)

        return type_hint, [field_representation]

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
        enum_name: str = casefy.pascalcase(field["name"])

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
        add_schema_name = enum_name != field["name"]
        metaclass = self.render_metaclass(
            schema=field,
            decorator=templates.METACLASS_DECORATOR,
            add_schema_name=add_schema_name,
        )

        if metaclass:
            enum_class += metaclass

        self.extras.append(enum_class)

        return enum_name

    def get_language_type(
        self,
        *,
        avro_type: str,
        field_name: typing.Optional[str] = None,
        default: typing.Optional[str] = None,
        model_name: typing.Optional[str] = None,
    ) -> str:
        if avro_type in (field_utils.INT, field_utils.FLOAT):
            self.imports.add("from dataclasses_avroschema import types")

        if avro_type == model_name:
            # it means that it is a one-to-self-relationship
            return templates.type_template.safe_substitute(type=avro_type)
        elif avro_type not in self.avro_type_to_lang:
            # it means the type points to the an already specified type so it contains the type name
            # with optional namespaces, e.g. my_namespace.users.User
            # In this case we should return the last part of the string
            type_hint = casefy.pascalcase(avro_type.split(".")[-1])

            if field_name == type_hint:
                type_hint = f"_{avro_type}"
            return type_hint
        elif default is not None:
            return str(self.avro_type_to_lang.get(avro_type, default))
        else:
            return str(self.avro_type_to_lang.get(avro_type, avro_type))

    @staticmethod
    def type_to_defined_types(avro_type: typing.Any) -> JsonDict:
        if isinstance(avro_type, (str, list)):
            avro_type = {"type": avro_type}

        return avro_type

    def get_field_metadata(self, field: JsonDict) -> JsonDict:
        keys_to_ignore = [
            "name",
            "type",
            "default",
            "pydantic-class",
            "precision",
            "scale",
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

    @staticmethod
    def _add_schema_to_metaclass(schema_template: Template, schema: JsonDict) -> str:
        """
        Parses provided schema to ModelGenerator.render() to a Meta field string by using
        metaclass_schema_field_template.
        """
        return schema_template.safe_substitute(name="original_schema", schema=json.dumps(schema))
