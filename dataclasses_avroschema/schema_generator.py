import dataclasses
import json
import typing
from collections import OrderedDict

from dacite import Config, from_dict

from dataclasses_avroschema import case, utils
from dataclasses_avroschema.schema_definition import AvroSchemaDefinition
from dataclasses_avroschema.serialization import deserialize, serialize, to_json
from dataclasses_avroschema.utils import SchemaMetadata, is_custom_type

from .fields import FieldType

AVRO = "avro"
AVRO_JSON = "avro-json"

JsonDict = typing.Dict[str, typing.Any]
CT = typing.TypeVar("CT", bound="AvroModel")


class AvroModel:

    schema_def: typing.Optional[AvroSchemaDefinition] = None
    klass: typing.Any = None
    metadata: typing.Optional[SchemaMetadata] = None
    user_defined_types: typing.Tuple[utils.UserDefinedType] = ()
    rendered_schema: typing.Optional[OrderedDict] = None

    @classmethod
    def generate_dataclass(cls: typing.Any) -> typing.Any:
        if dataclasses.is_dataclass(cls):
            return cls
        return dataclasses.dataclass(cls)

    @classmethod
    def generate_metadata(cls: typing.Any) -> SchemaMetadata:
        meta = getattr(cls.klass, "Meta", None)

        return SchemaMetadata.create(meta)

    @classmethod
    def generate_schema(cls: typing.Type[CT], schema_type: str = "avro") -> AvroSchemaDefinition:
        if cls.schema_def is None:
            # Generate metaclass and metadata
            cls.klass = cls.generate_dataclass()
            cls.metadata = cls.generate_metadata()

            # let's live open the possibility to define different
            # schema definitions like json
            if schema_type == "avro":
                # cache the schema
                cls.schema_def = cls._generate_avro_schema()
                cls.rendered_schema = cls.schema_def.render()
            else:
                raise ValueError("Invalid type. Expected avro schema type.")

        return cls.rendered_schema

    @classmethod
    def _generate_avro_schema(cls: typing.Any) -> AvroSchemaDefinition:
        return AvroSchemaDefinition("record", cls.klass, metadata=cls.metadata, parent=cls)

    @classmethod
    def avro_schema(cls: typing.Any, case_type: typing.Optional[str] = None) -> str:
        avro_schema = cls.generate_schema(schema_type=AVRO)

        # After generating the avro schema, reset the raw_fields to the init
        cls.user_defined_types = ()

        if case_type is not None:
            avro_schema = case.case_record(cls.rendered_schema, case_type)

        return json.dumps(avro_schema)

    @classmethod
    def avro_schema_to_python(cls: typing.Any) -> typing.Dict[str, typing.Any]:
        return json.loads(cls.avro_schema())

    @classmethod
    def get_fields(cls: typing.Any) -> typing.List[FieldType]:
        if cls.schema_def is None:
            cls.generate_schema()
        return cls.schema_def.fields

    @staticmethod
    def standardize_custom_type(value: typing.Any) -> typing.Any:
        if is_custom_type(value):
            return value["default"]
        return value

    def asdict(self) -> JsonDict:
        data = dataclasses.asdict(self)

        # te standardize called can be replaced if we have a custom implementation of asdict
        # for now I think is better to use the native implementation
        return {key: self.standardize_custom_type(value) for key, value in data.items()}

    def serialize(self, serialization_type: str = AVRO) -> bytes:
        schema = self.avro_schema_to_python()

        return serialize(self.asdict(), schema, serialization_type=serialization_type)

    @classmethod
    def deserialize(
        cls: typing.Type[CT],
        data: bytes,
        serialization_type: str = AVRO,
        create_instance: bool = True,
        writer_schema: typing.Optional[typing.Union[JsonDict, CT]] = None,
    ) -> typing.Union[JsonDict, CT]:

        try:
            writer_schema = writer_schema.avro_schema_to_python()
        except AttributeError:
            pass

        schema = cls.avro_schema_to_python()
        payload = deserialize(data, schema, serialization_type=serialization_type, writer_schema=writer_schema)

        if create_instance:
            return from_dict(data_class=cls, data=payload, config=Config(**cls.config()))
        return payload

    def to_json(self) -> JsonDict:
        # Serialize using the current AVRO schema to get proper field representations
        # and after that convert into python
        data = self.asdict()
        return to_json(data)

    @classmethod
    def config(cls) -> JsonDict:
        """
        Get the default config for dacite and always include the self reference
        """
        return {
            "check_types": False,
            "forward_references": {
                cls.klass.__name__: cls.klass,
            },
        }

    @classmethod
    def fake(cls: typing.Type[CT]) -> CT:
        payload = {field.name: field.fake() for field in cls.get_fields()}

        return from_dict(data_class=cls, data=payload, config=Config(**cls.config()))
