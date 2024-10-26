import dataclasses
import inspect
import typing
from collections import OrderedDict

from .fields.base import Field
from .utils import SchemaMetadata

if typing.TYPE_CHECKING:
    from .main import AvroModel


class Parser:
    """
    Parse python dataclasses to represent it as an avro schema.

    Each classes field is converted into an AvroField in order to
    be represented as an avro type.
    """

    def __init__(
        self,
        type: typing.Type["AvroModel"],
        parent: typing.Type["AvroModel"],
    ):
        self.type = type
        self.parent = parent

        # generate the dataclass for thr given type
        self.dataclass = self.generate_dataclass()

        meta = getattr(type, "Meta", type)
        self.metadata = SchemaMetadata.create(meta)
        exclude = self.metadata.exclude

        self.fields = self.parse_fields(exclude=exclude)
        self.fields_map = {field.name: field for field in self.fields}

    def generate_dataclass(self) -> typing.Type:
        from .main import AvroModel

        if self.type is AvroModel:
            raise AttributeError("Schema generation must be called on a subclass of AvroModel, not AvroModel itself.")

        if dataclasses.is_dataclass(self.type):
            return self.type
        return dataclasses.dataclass(self.type)

    def parse_fields(self, exclude: typing.List) -> typing.List[Field]:
        from .fields.fields import AvroField

        return [
            AvroField(
                dataclass_field.name,
                dataclass_field.type,
                default=dataclass_field.default,
                default_factory=dataclass_field.default_factory,  # type: ignore  # TODO: resolve mypy
                metadata=dict(dataclass_field.metadata),
                model_metadata=self.metadata,
                parent=self.parent,
            )
            for dataclass_field in dataclasses.fields(self.dataclass)
            if dataclass_field.name not in exclude
        ]

    def get_fields_map(self) -> typing.Dict[str, Field]:
        return self.fields_map

    def get_schema_name(self) -> str:
        return self.metadata.schema_name or self.type.__name__

    def generate_documentation(self) -> typing.Optional[str]:
        if isinstance(self.metadata.schema_doc, str):
            doc: typing.Optional[str] = self.metadata.schema_doc
        else:
            doc = self.type.__doc__
            # dataclasses create a (in avro context) useless docstring by default,
            # which we don't want in the schema.
            is_dataclass_with_default_docstring = (
                # from https://github.com/python/cpython/blob/3.10/Lib/dataclasses.py
                doc == (self.type.__name__ + str(inspect.signature(self.type)).replace(" -> None", ""))
            )
            if is_dataclass_with_default_docstring:
                return None

        if doc is not None:
            return doc.strip()
        return None

    def get_rendered_fields(self) -> typing.List[OrderedDict]:
        field_order = self.metadata.field_order

        if field_order is not None:
            for field_name in self.fields_map.keys():
                if field_name not in field_order:
                    field_order.append(field_name)

            return [self.fields_map[field_name].render() for field_name in field_order]
        return [field.render() for field in self.fields]

    def render(self) -> OrderedDict:
        schema = OrderedDict(
            [
                ("type", "record"),
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
