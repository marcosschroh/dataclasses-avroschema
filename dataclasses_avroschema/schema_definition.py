import abc
import dataclasses
import inspect
import typing
from collections import OrderedDict

from dataclasses_avroschema import fields

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
    klass_or_instance: typing.Any

    @abc.abstractmethod
    def get_rendered_fields(self):
        ...  # pragma: no cover

    @abc.abstractmethod
    def render(self):
        ...  # pragma: no cover

    def get_schema_name(self):
        if inspect.isclass(self.klass_or_instance):
            return self.klass_or_instance.__name__
        return self.klass_or_instance.__class__.__name__

    def generate_documentation(self):
        doc = self.klass_or_instance.__doc__

        if doc is not None:
            return doc.replace("\n", "")

    @property
    def is_faust_record(self) -> bool:
        if faust:
            if inspect.isclass(self.klass_or_instance):
                return issubclass(self.klass_or_instance, faust.Record)
            return issubclass(self.klass_or_instance.__class__, faust.Record)

        return False


@dataclasses.dataclass
class AvroSchemaDefinition(BaseSchemaDefinition):
    aliases: typing.List[str] = None
    namespace: str = None
    fields: typing.List["fields.FieldType"] = None
    include_schema_doc: bool = True

    def __post_init__(self):
        self.generate_extra_avro_attributes()
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
            for dataclass_field in dataclasses.fields(self.klass_or_instance)
        ]

    def parse_faust_record_fields(self) -> typing.List["fields.Field"]:
        schema_fields = []

        for dataclass_field in dataclasses.fields(self.klass_or_instance):
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

    def generate_extra_avro_attributes(self) -> None:
        """
        Look for the method in the dataclass.

        After calling the method extra_avro_attributes a dict is expected:
            typing.Dict[str, typing.Any]
        """
        extra_avro_attributes_fn = getattr(self.klass_or_instance, "extra_avro_attributes", None)

        if extra_avro_attributes_fn:
            extra_avro_attributes = extra_avro_attributes_fn()
            assert isinstance(extra_avro_attributes, dict), "Dict must be returned type in extra_avro_attributes method"

            aliases = extra_avro_attributes.get("aliases", self.aliases)
            namespace = extra_avro_attributes.get("namespace", self.namespace)

            self.aliases = aliases
            self.namespace = namespace

    def render(self):
        schema = OrderedDict(
            [("type", self.type), ("name", self.get_schema_name()), ("fields", self.get_rendered_fields()),]
        )

        if self.include_schema_doc:
            doc = self.generate_documentation()
            if doc is not None:
                schema["doc"] = doc

        if self.namespace is not None:
            schema["namespace"] = self.namespace

        if self.aliases is not None:
            schema["aliases"] = self.aliases

        return schema
