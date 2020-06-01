import abc
import dataclasses
import typing
from collections import OrderedDict

from dataclasses_avroschema import fields, utils

try:
    import faust
except ImportError:  # pragma: no cover
    faust = None  # pragma: no cover


@dataclasses.dataclass
class BaseSchemaDefinition(abc.ABC):
    """
    Minimal Schema definition
    """

    type: str
    klass: typing.Any

    @abc.abstractmethod
    def get_rendered_fields(self):
        ...  # pragma: no cover

    @abc.abstractmethod
    def render(self):
        ...  # pragma: no cover

    def get_schema_name(self):
        return self.klass.__name__

    def generate_documentation(self):
        doc = self.klass.__doc__

        if doc is not None:
            return doc.replace("\n", "")

    @property
    def is_faust_record(self) -> bool:
        if faust:
            return issubclass(self.klass, faust.Record)
        return False


@dataclasses.dataclass
class AvroSchemaDefinition(BaseSchemaDefinition):
    aliases: typing.List[str] = None
    namespace: str = None
    fields: typing.List["fields.FieldType"] = None
    metadata: utils.SchemaMetadata = None

    def __post_init__(self):
        self.fields = self.parse_dataclasses_fields()

    def parse_dataclasses_fields(self) -> typing.List["fields.Field"]:
        if self.is_faust_record:
            return self.parse_faust_record_fields()
        return self.parse_fields()

    def parse_fields(self):
        return [
            fields.Field(
                dataclass_field.name,
                dataclass_field.type,
                dataclass_field.default,
                dataclass_field.default_factory,
                dataclass_field.metadata,
            )
            for dataclass_field in dataclasses.fields(self.klass)
        ]

    def parse_faust_record_fields(self) -> typing.List["fields.Field"]:
        schema_fields = []

        for dataclass_field in dataclasses.fields(self.klass):
            faust_field = dataclass_field.default

            if faust_field.required:
                default = dataclasses.MISSING
                default_factory = dataclasses.MISSING
            else:
                default = faust_field.default
                default_factory = dataclasses.MISSING

                if isinstance(default, dataclasses.Field):
                    default_factory = default.default_factory
                    default = dataclasses.MISSING

            schema_fields.append(fields.Field(dataclass_field.name, dataclass_field.type, default, default_factory))

        return schema_fields

    def get_rendered_fields(self) -> typing.List["fields.Field"]:
        return [field.render() for field in self.fields]

    def render(self):
        schema = OrderedDict(
            [("type", self.type), ("name", self.get_schema_name()), ("fields", self.get_rendered_fields()),]
        )

        if self.metadata.schema_doc:
            doc = self.generate_documentation()
            if doc is not None:
                schema["doc"] = doc

        if self.metadata.namespace is not None:
            schema["namespace"] = self.metadata.namespace

        if self.metadata.aliases is not None:
            schema["aliases"] = self.metadata.aliases

        return schema
