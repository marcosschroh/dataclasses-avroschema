import dataclasses
import json
import typing

from dataclasses_avroschema import schema_definition, serialization, utils

AVRO = "avro"
AVRO_JSON = "avro-json"


class AvroModel:

    schema_def: schema_definition.AvroSchemaDefinition = None
    klass: typing.Any = None
    metadata: typing.Dict = None

    @classmethod
    def generate_dataclass(cls):
        if dataclasses.is_dataclass(cls):
            return cls
        return dataclasses.dataclass(cls)

    @classmethod
    def generate_metadata(cls):
        meta = getattr(cls.klass, "Meta", None)

        if meta is None:
            return utils.SchemaMetadata()
        return utils.SchemaMetadata.create(meta)

    @classmethod
    def generate_schema(cls, schema_type: str = "avro"):
        if cls.schema_def is not None:
            return cls.schema_def.render()

        # Generate metaclass and metadata
        cls.klass = cls.generate_dataclass()
        cls.metadata = cls.generate_metadata()

        # let's live open the possibility to define different
        # schema definitions like json
        if schema_type == "avro":
            # cache the schema
            cls.schema_def = cls._generate_avro_schema()
        else:
            raise ValueError("Invalid type. Expected avro schema type.")

        return cls.schema_def.render()

    @classmethod
    def _generate_avro_schema(cls) -> schema_definition.AvroSchemaDefinition:
        return schema_definition.AvroSchemaDefinition("record", cls.klass, metadata=cls.metadata)

    @classmethod
    def avro_schema(cls) -> str:
        return json.dumps(cls.generate_schema(schema_type=AVRO))

    @classmethod
    def avro_schema_to_python(cls) -> typing.Dict[str, typing.Any]:
        return json.loads(cls.avro_schema())

    @classmethod
    def get_fields(cls) -> typing.List["schema_definition.Field"]:
        if cls.schema_def is None:
            cls.generate_schema()

        return cls.schema_def.fields

    def serialize(self, serialization_type: str = AVRO) -> bytes:
        data = dataclasses.asdict(self)
        schema = self.avro_schema_to_python()

        return serialization.serialize(data, schema, serialization_type=serialization_type)

    @classmethod
    def deserialize(cls, data: bytes, serialization_type: str = AVRO) -> typing.Any:
        schema = cls.avro_schema_to_python()

        return serialization.deserialize(data, schema, serialization_type=serialization_type)

    def to_json(self):
        data = self.serialize(serialization_type=AVRO_JSON)

        return json.loads(data.decode())
