from __future__ import annotations

import dataclasses
import typing
from collections import OrderedDict

from pydantic.fields import FieldInfo

from dataclasses_avroschema.fields.base import Field
from dataclasses_avroschema.fields.fields import AvroField
from dataclasses_avroschema.parser import Parser


def pydantic_to_avro_field(field_name: str, field_info: FieldInfo, parser: PydanticParser) -> Field:
    metadata = field_info.json_schema_extra.get("metadata", {}) if field_info.json_schema_extra else {}
    if field_info.description:
        metadata["doc"] = field_info.description

    return AvroField(
        field_name,
        field_info.rebuild_annotation(),
        default=dataclasses.MISSING if field_info.is_required() or field_info.default_factory else field_info.default,
        default_factory=field_info.default_factory,
        metadata=metadata,
        model_metadata=parser.metadata,
        parent=parser.parent,
    )


class PydanticParser(Parser):
    def parse_fields(self, exclude: typing.List) -> typing.List[Field]:
        return [
            pydantic_to_avro_field(field_name, field_info, self)
            for field_name, field_info in self.type.model_fields.items()
            if field_name not in exclude and field_name != "model_config"
        ]

    def render(self) -> OrderedDict:
        schema = super().render()
        if "doc" not in schema and self.type.model_config and "title" in self.type.model_config:
            schema["doc"] = self.type.model_config["title"]
        return schema
