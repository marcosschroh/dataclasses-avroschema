import dataclasses
import typing

from dataclasses_avroschema.fields.base import Field
from dataclasses_avroschema.fields.fields import AvroField
from dataclasses_avroschema.parser import Parser


class PydanticParser(Parser):
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
