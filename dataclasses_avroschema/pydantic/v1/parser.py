import dataclasses
import typing

from dataclasses_avroschema.fields.base import Field
from dataclasses_avroschema.fields.fields import AvroField
from dataclasses_avroschema.parser import Parser

if typing.TYPE_CHECKING:
    from .main import AvroBaseModel  # pragma: no cover


class PydanticV1Parser(Parser):
    def __init__(
        self,
        type,
        parent,
    ):
        super().__init__(type, parent)
        self.type: typing.Type["AvroBaseModel"]
        self.parent: typing.Type["AvroBaseModel"]

    def generate_dataclass(self) -> typing.Type:
        return self.type

    def parse_fields(self, exclude: typing.List) -> typing.List[Field]:
        return [
            AvroField(
                model_field.name,
                model_field.annotation,
                default=dataclasses.MISSING
                if model_field.required or model_field.default_factory
                else model_field.default,
                default_factory=model_field.default_factory,
                metadata=model_field.field_info.extra.get("metadata", {}),
                model_metadata=self.metadata,
                parent=self.parent,
            )
            for model_field in self.type.__fields__.values()
            if model_field.name not in exclude
        ]
