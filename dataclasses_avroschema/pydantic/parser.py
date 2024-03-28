from __future__ import annotations

import dataclasses
import typing

from pydantic.fields import FieldInfo

from dataclasses_avroschema.fields.base import Field
from dataclasses_avroschema.fields.fields import AvroField
from dataclasses_avroschema.parser import Parser


class PydanticParser(Parser):
    @staticmethod
    def get_field_metadata(field_info: FieldInfo) -> dict[str, typing.Any]:
        metadata: dict[str, typing.Any] = (
            field_info.json_schema_extra.get("metadata", {}) if field_info.json_schema_extra else {}  # type: ignore
        )
        if field_info.description:
            metadata["doc"] = field_info.description  # type: ignore

        aliases = set(metadata.get("aliases", []))

        if field_info.alias is not None:
            aliases.add(field_info.alias)
        if field_info.serialization_alias is not None:
            aliases.add(field_info.serialization_alias)
        if aliases:
            metadata["aliases"] = list(aliases)

        return metadata

    def parse_fields(self, exclude: typing.List) -> typing.List[Field]:
        return [
            AvroField(
                field_name,
                field_info.rebuild_annotation(),
                default=dataclasses.MISSING
                if field_info.is_required() or field_info.default_factory
                else field_info.default,
                default_factory=field_info.default_factory,
                metadata=self.get_field_metadata(field_info),
                model_metadata=self.metadata,
                parent=self.parent,
            )
            for field_name, field_info in self.type.model_fields.items()
            if field_name not in exclude and field_name != "model_config"
        ]

    def generate_documentation(self) -> typing.Optional[str]:
        doc = None
        if isinstance(self.metadata.schema_doc, str):
            doc = self.metadata.schema_doc
        elif self.type.model_config and "title" in self.type.model_config:
            doc = self.type.model_config["title"]
        else:
            doc = super().generate_documentation()
        return doc
