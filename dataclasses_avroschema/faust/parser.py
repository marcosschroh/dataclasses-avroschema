import dataclasses
import typing

from dataclasses_avroschema.fields.base import Field
from dataclasses_avroschema.fields.fields import AvroField
from dataclasses_avroschema.parser import Parser


class FaustParser(Parser):
    def parse_fields(self, exclude: typing.List) -> typing.List[Field]:
        schema_fields = []

        for dataclass_field in dataclasses.fields(self.type):
            if dataclass_field.name in exclude:
                continue

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
                        metadata=dict(metadata),
                        model_metadata=self.metadata,
                        parent=self.parent,
                    )
                )

        return schema_fields
