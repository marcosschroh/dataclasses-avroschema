import dataclasses
import typing

from dataclasses_avroschema.fields.base import Field
from dataclasses_avroschema.fields.fields import AvroField
from dataclasses_avroschema.parser import Parser


class PydanticParser(Parser):
    def parse_fields(self, exclude: typing.List) -> typing.List[Field]:
        return [
            AvroField(
                field_name,
                field_info.rebuild_annotation(),
                default=dataclasses.MISSING
                if field_info.is_required() or field_info.default_factory
                else field_info.default,
                default_factory=field_info.default_factory,
                metadata=field_info.json_schema_extra.get("metadata", {}) if field_info.json_schema_extra else {},
                model_metadata=self.metadata,
                parent=self.parent,
            )
            for field_name, field_info in self.type.model_fields.items()
            if field_name not in exclude and field_name != "model_config"
        ]
