import copy
import dataclasses
import typing
from dataclasses import dataclass, field
from string import Template

import casefy
import fastavro

from dataclasses_avroschema import serialization
from dataclasses_avroschema.fields import field_utils
from dataclasses_avroschema.types import JsonDict

from . import avro_to_python_utils, templates
from .base_class import BaseClassEnum


class FieldRepresentation(typing.NamedTuple):
    name: str
    string_representation: str
    has_default: bool


@dataclass
class ModelGenerator:
    base_class: str = BaseClassEnum.AVRO_MODEL.value
    field_identation: str = "\n    "
    imports: typing.Set[str] = field(default_factory=set)
    imports_dict: typing.Dict[str, str] = field(default_factory=dict)

    # extras is used fot extra code that is generated, for example Enums
    extras: typing.List[str] = field(default_factory=list)

    class_template: Template = templates.class_template
    dataclass_field_template: Template = templates.dataclass_field_template
    metadata_fields_mapper: typing.Dict[str, str] = field(
        default_factory=lambda: {
            # doc is not included because it is rendered as docstrings
            "namespace": "namespace",
            "aliases": "aliases",
        }
    )
    matadata_field_templates: typing.Dict[str, Template] = field(
        default_factory=lambda: {
            "namespace": templates.metaclass_field_template,
            "doc": templates.metaclass_field_template,
            "aliases": templates.metaclass_alias_field_template,
        }
    )
    # represent the decorator to add in the base class
    base_class_decotator: str = ""
    avro_type_to_python: typing.Dict[str, str] = field(init=False)
    logical_types_imports: typing.Dict[str, str] = field(init=False)

    def __post_init__(self) -> None:
        # add the base class import
        base_class_to_imports = {
            BaseClassEnum.AVRO_MODEL.value: "from dataclasses_avroschema import AvroModel",
            BaseClassEnum.PYDANTIC_MODEL.value: "from pydantic import BaseModel",
            BaseClassEnum.AVRO_DANTIC_MODEL.value: "from dataclasses_avroschema.avrodantic import AvroBaseModel",
        }
        self.imports.add(base_class_to_imports[self.base_class])

        self.avro_type_to_python = avro_to_python_utils.AVRO_TYPE_TO_PYTHON
        self.logical_types_imports = avro_to_python_utils.LOGICAL_TYPES_IMPORTS

        if self.base_class == BaseClassEnum.AVRO_MODEL.value:
            self.imports.add("import dataclasses")
            self.base_class_decotator = "@dataclasses.dataclass"
            self.imports_dict = {
                "dataclass_field": "import dataclasses",
                "condecimal": "from dataclasses_avroschema.types import condecimal",
            }
        else:
            self.dataclass_field_template = templates.pydantic_field_template
            self.imports_dict = {
                "dataclass_field": "from pydantic import Field",
                "condecimal": "from pydantic import condecimal",
            }

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

    def render_metaclass(
        self, *, schema: JsonDict, field_order: typing.Optional[typing.List[str]] = None
    ) -> typing.Optional[str]:
        """
        Render Class Meta that contains the schema matadata
        """
        metadata = [
            self.matadata_field_templates[meta_avro_field].safe_substitute(
                name=meta_field, value=schema.get(meta_avro_field)
            )
            for meta_avro_field, meta_field in self.metadata_fields_mapper.items()
            if schema.get(
                meta_avro_field
            )  # TODO: replace this line with if (value := schema.get(meta_avro_field)) after drop py3.7
        ]

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
            return (
                self.field_identation.join(
                    [line for line in templates.metaclass_template.safe_substitute(properties=properties).split("\n")]
                ).rstrip(self.field_identation)
                + "\n"
            )
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
            decorator=self.base_class_decotator,
            base_class=self.base_class,
            fields=rendered_fields_string,
            docstring=docstring,
        )

        class_metadata = self.render_metaclass(schema=schema, field_order=field_order)
        if class_metadata is not None:
            rendered_class += class_metadata

        return rendered_class

    def render_dataclass_field(self, properties: str) -> str:
        self.imports.add(self.imports_dict["dataclass_field"])

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

    def render_field(self, field: JsonDict, model_name: str) -> FieldRepresentation:
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
        default = field.get("default", dataclasses.MISSING)
        field_metadata = self.get_field_metadata(field)

        # This flag tells whether the field is array, map, fixed
        is_complex_type = False

        if self.is_logical_type(field=field):
            is_complex_type = True
            # override the type so it can be use to get the default value in case that is needed
            type = field.get("logicalType") or field["type"]["logicalType"]
            language_type = self.parse_logical_type(field=field)
        elif isinstance(type, dict):
            field_representation = self.render_field(field=type, model_name=model_name)
            language_type = field_representation.string_representation
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
            result = templates.field_template.safe_substitute(name=name, type=language_type)

        # optional field attribute
        default = self.get_field_default(field_type=type, default=default, name=name, field_metadata=field_metadata)

        has_default = False
        if default is not dataclasses.MISSING:
            has_default = True

            if type != field_utils.DECIMAL:
                result += templates.field_default_template.safe_substitute(default=default)

        return FieldRepresentation(name=name, string_representation=result, has_default=has_default)

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
            type = self.avro_type_to_python[logical_type]

        if field_name is not None:
            field_repr = templates.field_template.safe_substitute(name=field_name, type=type)
            return field_repr

        return type

    def parse_decimal(self, *, field: JsonDict, default: typing.Optional[str] = None) -> str:
        precision = field["precision"]
        scale = field["scale"]

        self.imports.add(self.imports_dict["condecimal"])
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

        field_name: str = field["name"]
        enum_name = casefy.pascalcase(field_name)

        symbols_map = {}
        for symbol in field["symbols"]:
            key = casefy.uppercase(symbol)
            if key in symbols_map:
                key = symbol
            symbols_map[key] = symbol

        symbols = self.field_identation.join(
            [
                templates.enum_symbol_template.safe_substitute(key=key, value=f'"{value}"')
                for key, value in symbols_map.items()
            ]
        )
        docstring = self.render_docstring(docstring=field.get("doc"))

        enum_class = templates.enum_template.safe_substitute(name=enum_name, symbols=symbols, docstring=docstring)
        self.extras.append(enum_class)

        return enum_name

    def _get_complex_langauge_type(self, *, type: typing.Any, model_name: str) -> str:
        """
        Get the language type for complext types (array and maps)
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
        self, *, type: str, default: typing.Optional[str] = None, model_name: typing.Optional[str] = None
    ) -> str:
        if type in (field_utils.INT, field_utils.FLOAT):
            self.imports.add("from dataclasses_avroschema import types")

        if type == model_name:
            # it means that it is a one-to-self-relationship
            return templates.type_template.safe_substitute(type=type)

        if default is not None:
            return str(self.avro_type_to_python.get(type, default))
        return str(self.avro_type_to_python.get(type, type))

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
        """
        Check if the language type must be replaced with any extra class which
        was specified in the field metadata. This method should be only called
        after the native type was resolved properly.

        An example of this if when a pydantic field was used in the model:

        class MyModel(AvroBaseModel):
            email: pydantic.EmailStr

        then the email field is represented as:

        {"name": "email", "type": {"type": "string", "pydantic-class": "EmailStr"}}

        For now we only recognize the attribute `pydantic-class` but in the future
        new way might be added, for example: `java-class`.

        """
        if self.base_class in (
            BaseClassEnum.AVRO_DANTIC_MODEL.value,
            BaseClassEnum.PYDANTIC_MODEL.value,
        ):
            pydantic_class = field.get("pydantic-class")

            if pydantic_class is not None:
                self.imports.add("import pydantic")
                return f"pydantic.{pydantic_class}"
        return None

    def get_field_default(
        self, *, field_type: str, default: typing.Any, name: str, field_metadata: typing.Optional[JsonDict] = None
    ) -> typing.Any:
        """
        Returns the default value according to the field type

        TODO: docstrings

        Example:
            If the default is "bond" the method should return '"bond"' so the double quotes
            won't be scaped during the field render
        """
        dataclass_field_default_factory = dataclass_field_metadata = None
        if field_metadata:
            dataclass_field_metadata = f"metadata={field_metadata}"

        if default is dataclasses.MISSING:
            # we do not do anything, just check dataclasses.field properties
            pass
        elif field_type in (field_utils.STRING, field_utils.UUID):
            default = f'"{default}"'
        elif field_type == field_utils.BYTES:
            default = f'b"{default}"'
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
                dataclass_field_default_factory = f"default_factory=lambda: {default}"
            else:
                # it is an array or maps with `[]` or `{} ` as default
                dataclass_field_default_factory = f"default_factory={default.__class__.__name__}"
        elif isinstance(field_type, dict):
            inner_type = field_type["type"]
            name = field_type.get("name", name)
            default = self.get_field_default(field_type=inner_type, name=name, default=default)
        elif field_type == field_utils.ENUM:
            default = f"{casefy.pascalcase(name)}.{casefy.uppercase(default)}"
        elif isinstance(field_type, list):
            default = self.get_field_default(field_type=field_type[0], default=default, name=name)
        elif field_type in avro_to_python_utils.LOGICAL_TYPES_TO_PYTHON:
            func = avro_to_python_utils.LOGICAL_TYPES_TO_PYTHON[field_type]
            python_type = func(default)
            template_func = avro_to_python_utils.LOGICAL_TYPE_TEMPLATES[field_type]
            default = template_func(python_type)
        else:
            default = default

        dataclass_field_properties = [
            dataclass_field_default_factory,
            dataclass_field_metadata,
        ]

        if any(dataclass_field_properties):
            # If the default was not set or the default_factory was set
            # then we not need a default in the field
            if default is not dataclasses.MISSING and dataclass_field_default_factory is None:
                dataclass_field_properties.append(f" default={default}")

            default = self.render_dataclass_field(
                properties=",".join([prop for prop in dataclass_field_properties if prop is not None])
            )

        return default
