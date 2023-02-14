import abc
import dataclasses
import typing
from collections import OrderedDict

from dataclasses_avroschema import utils
from dataclasses_avroschema.fields import AvroField, FieldType


@dataclasses.dataclass  # type: ignore
class BaseSchemaDefinition(abc.ABC):
    """
    Minimal Schema definition
    """

    __slots__ = (
        "type",
        "klass",
        "parent",
        "matadata",
    )

    type: str
    klass: typing.Any
    parent: typing.Any
    metadata: utils.SchemaMetadata

    @abc.abstractmethod
    def get_rendered_fields(self) -> typing.List[OrderedDict]:
        ...  # pragma: no cover

    @abc.abstractmethod
    def render(self) -> OrderedDict:
        ...  # pragma: no cover

    def get_schema_name(self) -> str:
        return self.klass.metadata.schema_name or self.klass.__name__

    def generate_documentation(self) -> typing.Optional[str]:
        if isinstance(self.metadata.schema_doc, str):
            doc = self.metadata.schema_doc
        else:
            doc = self.klass.__doc__

        if doc is not None:
            return doc.replace("\n", "")
        return None


@dataclasses.dataclass
class AvroSchemaDefinition(BaseSchemaDefinition):
    fields: typing.List[FieldType] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        self.fields = self.parse_dataclasses_fields()

    def parse_dataclasses_fields(self) -> typing.List[FieldType]:
        if utils.is_faust_model(self.klass):
            return self.parse_faust_fields()
        elif utils.is_pydantic_model(self.klass):
            return self.parse_pydantic_fields()
        return self.parse_fields()

    def parse_fields(self) -> typing.List[FieldType]:
        return [
            AvroField(
                dataclass_field.name,
                dataclass_field.type,
                default=dataclass_field.default,
                default_factory=dataclass_field.default_factory,  # type: ignore  # TODO: resolve mypy
                metadata=dataclass_field.metadata,
                model_metadata=self.metadata,
                parent=self.parent,
            )
            for dataclass_field in dataclasses.fields(self.klass)
        ]

    def parse_faust_fields(self) -> typing.List[FieldType]:
        schema_fields = []

        for dataclass_field in dataclasses.fields(self.klass):
            faust_field = dataclass_field.default
            metadata = dataclass_field.metadata
            default_factory = dataclasses.MISSING

            if faust_field is not dataclasses.MISSING:
                if faust_field.required:
                    default = dataclasses.MISSING
                else:
                    default = faust_field.default

                    if isinstance(default, dataclasses.Field):
                        metadata = default.metadata
                        default_factory = default.default_factory  # type: ignore  # TODO: resolve mypy
                        default = dataclasses.MISSING

                schema_fields.append(
                    AvroField(
                        dataclass_field.name,
                        dataclass_field.type,
                        default=default,
                        default_factory=default_factory,
                        metadata=metadata,
                        model_metadata=self.metadata,
                        parent=self.parent,
                    )
                )

        return schema_fields

    def parse_pydantic_fields(self) -> typing.List[FieldType]:
        return [
            AvroField(
                model_field.name,
                model_field.annotation,
                default=dataclasses.MISSING
                if model_field.required or model_field.default_factory
                else model_field.default,
                default_factory=model_field.default_factory,
                metadata=getattr(model_field, "metadata", {}),
                model_metadata=self.metadata,
                parent=self.parent,
            )
            for model_field in self.klass.__fields__.values()
        ]

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
