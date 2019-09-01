import json
import dataclasses
import typing

from .fields import Field
from .schema_definition import AvroSchemaDefinition


class SchemaGenerator:

    def __init__(self, klass_or_instance, schema_definition: str = "avro", include_schema_doc: bool = True) -> None:
        self.dataclass = self.generate_dataclass(klass_or_instance)
        self.fields = self.parse_dataclasses_fields()
        self.schema_definition = schema_definition
        self.include_schema_doc = include_schema_doc

    @staticmethod
    def generate_dataclass(klass_or_instance):
        if dataclasses.is_dataclass(klass_or_instance):
            return klass_or_instance
        return dataclasses.dataclass(klass_or_instance)

    def parse_dataclasses_fields(self) -> typing.List[Field]:
        return [
            Field(dataclass_field.name, dataclass_field.type, dataclass_field.default)
            for dataclass_field in dataclasses.fields(self.dataclass)
        ]

    def generate_schema(self):
        schema = AvroSchemaDefinition(
            "record",
            self.fields,
            self.dataclass,
            include_schema_doc=self.include_schema_doc
        ).render()

        return schema

    def avro_schema(self) -> str:
        return json.dumps(self.generate_schema())

    def to_python(self) -> typing.Dict[str, typing.Any]:
        return json.loads(self.avro_schema())

    @property
    def get_fields(self) -> typing.List[Field]:
        return self.fields
