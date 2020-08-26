import abc
import dataclasses
import typing
from collections import OrderedDict

from dataclasses_avroschema import utils
from dataclasses_avroschema.fields import AvroField, FieldType

try:
    import faust
except ImportError:  # pragma: no cover
    faust = None  # type: ignore # pragma: no cover


@dataclasses.dataclass  # type: ignore
class BaseSchemaDefinition(abc.ABC):
    """
    Minimal Schema definition
    """

    type: str
    klass: typing.Any

    @abc.abstractmethod
    def get_rendered_fields(self) -> typing.List[OrderedDict]:
        ...  # pragma: no cover

    @abc.abstractmethod
    def render(self) -> OrderedDict:
        ...  # pragma: no cover

    def get_schema_name(self) -> str:
        return self.klass.__name__

    def generate_documentation(self) -> typing.Optional[str]:
        doc = self.klass.__doc__

        return doc.replace("\n", "")

    @property
    def is_faust_record(self) -> bool:
        if faust:
            return issubclass(self.klass, faust.Record)
        return False


@dataclasses.dataclass
class AvroSchemaDefinition(BaseSchemaDefinition):
    aliases: typing.List[str] = dataclasses.field(default_factory=list)
    namespace: typing.Optional[str] = None
    fields: typing.List[FieldType] = dataclasses.field(default_factory=list)
    metadata: utils.SchemaMetadata = dataclasses.field(default_factory=utils.SchemaMetadata)

    def __post_init__(self) -> None:
        self.fields = self.parse_dataclasses_fields()

    def parse_dataclasses_fields(self) -> typing.List[FieldType]:
        if self.is_faust_record:
            return self.parse_faust_record_fields()
        return self.parse_fields()

    def parse_fields(self) -> typing.List[FieldType]:
        return [
            AvroField(
                dataclass_field.name,
                dataclass_field.type,
                dataclass_field.default,
                dataclass_field.default_factory,  # type: ignore  # TODO: resolve mypy
                dataclass_field.metadata,
            )
            for dataclass_field in dataclasses.fields(self.klass)
        ]

    def parse_faust_record_fields(self) -> typing.List[FieldType]:
        schema_fields = []

        for dataclass_field in dataclasses.fields(self.klass):
            faust_field = dataclass_field.default
            default_factory = dataclasses.MISSING

            if faust_field.required:
                default = dataclasses.MISSING
            else:
                default = faust_field.default

                if isinstance(default, dataclasses.Field):
                    default_factory = default.default_factory  # type: ignore  # TODO: resolve mypy
                    default = dataclasses.MISSING

            schema_fields.append(AvroField(dataclass_field.name, dataclass_field.type, default, default_factory))

        return schema_fields

    def get_rendered_fields(self) -> typing.List[OrderedDict]:
        return [field.render() for field in self.fields]

    def render(self) -> OrderedDict:
        schema = OrderedDict(
            [
                ("type", self.type),
                ("name", self.get_schema_name()),
                ("fields", self.get_rendered_fields()),
            ]
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
