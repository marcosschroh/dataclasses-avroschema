import dataclasses
import json
import typing


from dataclasses_avroschema import schema_definition, serialization


class SchemaGenerator:
    def __init__(self, klass_or_instance, include_schema_doc: bool = True) -> None:
        self.dataclass = self.generate_dataclass(klass_or_instance)
        self.include_schema_doc = include_schema_doc
        self.schema_definition: schema_definition.AvroSchemaDefinition = None

    @staticmethod
    def generate_dataclass(klass_or_instance):
        if dataclasses.is_dataclass(klass_or_instance):
            return klass_or_instance
        return dataclasses.dataclass(klass_or_instance)

    def generate_schema(self, schema_type: str = "avro"):
        if self.schema_definition is not None:
            return self.schema_definition.render()

        # let's live open the possibility to define different
        # schema definitions like json
        if schema_type == "avro":
            schema_def = self._generate_avro_schema()
        else:
            raise ValueError("Invalid type. Expected avro schema type.")

        # cache the schema
        self.schema_definition = schema_def

        return self.schema_definition.render()

    def _generate_avro_schema(self) -> schema_definition.AvroSchemaDefinition:
        return schema_definition.AvroSchemaDefinition(
            "record", self.dataclass, include_schema_doc=self.include_schema_doc
        )

    def avro_schema(self) -> str:
        return json.dumps(self.generate_schema(schema_type="avro"))

    def avro_schema_to_python(self) -> typing.Dict[str, typing.Any]:
        return json.loads(self.avro_schema())

    @property
    def get_fields(self) -> typing.List["schema_definition.Field"]:
        if self.schema_definition is None:
            self.generate_schema()

        return self.schema_definition.fields

    def serialize(self, serialization_type: str = "avro") -> bytes:
        data = dataclasses.asdict(self.dataclass)
        schema = self.avro_schema_to_python()

        return serialization.serialize(data, schema, serialization_type=serialization_type)

    def deserialize(self, data: bytes, serialization_type: str = "avro") -> typing.Any:
        schema = self.avro_schema_to_python()

        return serialization.deserialize(data, schema, serialization_type=serialization_type)
