import dataclasses
import enum
import inspect
import json
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union, ForwardRef

from dacite import Config, from_dict
from fastavro.validation import validate

from . import case, fields, serialization
from .schema_definition import AvroSchemaDefinition
from .types import Fixed, JsonDict
from .utils import SchemaMetadata, is_dataclass_or_pydantic_model

AVRO = "avro"
AVRO_JSON = "avro-json"


CT = TypeVar("CT", bound="AvroModel")


class AvroModel:
    schema_def: Optional[AvroSchemaDefinition] = None
    klass: Optional[Type] = None
    metadata: Optional[SchemaMetadata] = None
    user_defined_types: Set = set()
    parent: Any = None
    rendered_schema: OrderedDict = dataclasses.field(default_factory=OrderedDict)

    @classmethod
    def generate_dataclass(cls: Type[CT]) -> Type[CT]:
        if is_dataclass_or_pydantic_model(cls):
            return cls
        return dataclasses.dataclass(cls)

    @classmethod
    def generate_metadata(cls: Type[CT]) -> SchemaMetadata:
        meta = getattr(cls.klass, "Meta", type)

        return SchemaMetadata.create(meta)

    @classmethod
    def generate_schema(cls: Type[CT], schema_type: str = "avro") -> Optional[OrderedDict]:
        if cls.schema_def is None or cls.__mro__[1] != AvroModel:
            # Generate dataclass and metadata
            cls.klass = cls.generate_dataclass()

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
    def _generate_avro_schema(cls: Type[CT]) -> AvroSchemaDefinition:
        metadata = cls.generate_metadata()
        cls.metadata = metadata
        return AvroSchemaDefinition("record", cls.klass, metadata=metadata, parent=cls.parent or cls)

    @classmethod
    def avro_schema(cls: Type[CT], case_type: Optional[str] = None) -> str:
        return json.dumps(cls.avro_schema_to_python(case_type=case_type))

    @classmethod
    def avro_schema_to_python(
        cls: Type[CT], parent: Optional["AvroModel"] = None, case_type: Optional[str] = None
    ) -> Dict[str, Any]:
        if parent is not None:
            # in this case the current class is a child with a parent
            # we recalculate the schema definition to prevent re usages
            cls.parent = parent
            cls.schema_def = None
        else:
            # This happens when an AvroModel is the root of the tree (first class in the hierarchy)
            # Because intermediate schemas can be reused as a root later, we need to reset them
            # Example with A as a root:
            #     A -> B -> C -> D
            #
            # After generating the A.avro_schema the parent of B is A,
            # if we want to do B.avro_schema (now B is the root)
            # B should clean the data that was only valid when it was the child
            cls._reset_schema_definition()

        avro_schema = cls.generate_schema(schema_type=AVRO)

        if case_type is not None:
            avro_schema = case.case_record(cls.rendered_schema, case_type)  # type: ignore

        return json.loads(json.dumps(avro_schema))

    @classmethod
    def get_fields(cls: Type[CT]) -> List[fields.FieldType]:
        if cls.schema_def is None:
            cls.generate_schema()
        return cls.schema_def.fields  # type: ignore

    @classmethod
    def _get_enum_type_map(cls: Type[CT]) -> Dict[str, enum.EnumMeta]:
        enum_types = {}
        for field_type in cls.get_fields():
            if isinstance(field_type, fields.EnumField):
                enum_types[field_type.name] = field_type.type
            elif isinstance(field_type, fields.UnionField):
                for sub_type in field_type.type.__args__:
                    if inspect.isclass(sub_type) and issubclass(sub_type, enum.Enum):
                        enum_types[field_type.name] = sub_type
            elif isinstance(field_type, fields.RecordField):
                enum_types.update(field_type.type._get_enum_type_map())
        return enum_types

    @classmethod
    def _deserialize_list(cls: Type[CT], field: str, payload: Any) -> List:
        field_def = cls.schema_def.fields_map[field]
        item_type = field_def.type.__args__[0]  # it could be List[SOMETHING] or Tuple[Something]
        forward_type = Type[ForwardRef(field_def.parent.__name__)]

        if item_type == forward_type:  # recurcive case
            return [field_def.parent._deserialize_complex_types(v) for v in payload]
        elif issubclass(item_type, AvroModel):
            return [field_def.type.__args__[0]._deserialize_complex_types(v) for v in payload]
        else:
            return [v for v in payload]

    @classmethod
    def _deserialize_complex_types(cls: Type[CT], payload: Dict[str, Any]) -> Dict:
        output: Dict[str, Any] = {}
        enum_type_map = cls._get_enum_type_map()
        for field, value in payload.items():
            field_def = cls.schema_def.fields_map[field]
            if isinstance(field_def, fields.ListField):
                output[field] = cls._deserialize_list(field, value)
            if isinstance(field_def, fields.TupleField):
                output[field] = tuple(cls._deserialize_list(field, value))
            elif isinstance(field_def, fields.RecordField):
                record_type = field_def.type
                output[field] = record_type._deserialize_complex_types(value)
            elif field in enum_type_map and isinstance(value, str):
                try:
                    enum_field = enum_type_map[field]
                    output[field] = enum_field(value)
                except ValueError as e:
                    raise ValueError(f"Value {value} is not a valid instance of {enum_type_map[field]}", e)
            else:
                output[field] = value
        return output

    @classmethod
    def _reset_schema_definition(cls: Type[CT]) -> None:
        """
        Reset all the values to original state.
        """
        cls.user_defined_types = set()
        cls.schema_def = None
        cls.parent = None

    @staticmethod
    def standardize_custom_type(value: Any) -> Any:
        if isinstance(value, Fixed):
            return value.default
        elif isinstance(value, dict):
            return {k: AvroModel.standardize_custom_type(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [AvroModel.standardize_custom_type(v) for v in value]
        elif isinstance(value, tuple):
            return tuple(AvroModel.standardize_custom_type(v) for v in value)
        elif issubclass(type(value), enum.Enum):
            return value.value
        return value

    def asdict(self) -> JsonDict:
        return dataclasses.asdict(  # type: ignore
            self, dict_factory=lambda x: {key: self.standardize_custom_type(value) for key, value in x}
        )

    def serialize(self, serialization_type: str = AVRO) -> bytes:
        schema = self.avro_schema_to_python()

        return serialization.serialize(self.asdict(), schema, serialization_type=serialization_type)

    @classmethod
    def deserialize(
        cls: Type[CT],
        data: bytes,
        serialization_type: str = AVRO,
        create_instance: bool = True,
        writer_schema: Optional[Union[JsonDict, Type[CT]]] = None,
    ) -> Union[JsonDict, CT]:
        if inspect.isclass(writer_schema) and issubclass(writer_schema, AvroModel):
            # mypy does not undersdtand redefinitions
            writer_schema: JsonDict = writer_schema.avro_schema_to_python()  # type: ignore

        schema = cls.avro_schema_to_python()
        payload = serialization.deserialize(
            data, schema, serialization_type=serialization_type, writer_schema=writer_schema  # type: ignore
        )
        output = cls._deserialize_complex_types(payload)

        if create_instance:
            return cls.parse_obj(output)
        return output

    @classmethod
    def parse_obj(cls: Type[CT], data: Dict) -> Union[JsonDict, CT]:
        return from_dict(data_class=cls, data=data, config=Config(**cls.config()))

    def validate(self) -> bool:
        schema = self.avro_schema_to_python()
        return validate(self.asdict(), schema)

    def to_dict(self) -> JsonDict:
        # Serialize using the current AVRO schema to get proper field representations
        # and after that convert into python
        return self.asdict()

    def to_json(self) -> str:
        data = serialization.to_json(self.asdict())
        return json.dumps(data)

    @classmethod
    def config(cls: Type[CT]) -> JsonDict:
        """
        Get the default config for dacite and always include the self reference
        """
        # We need to make sure that the `avro schemas` has been generated, otherwise cls.klass is empty
        # It won't affect the performance because the rendered schema will be store in cls.rendered_schema
        cls.generate_schema()
        dacite_user_config = cls.metadata.dacite_config  # type: ignore

        dacite_config = {
            "check_types": False,
            "forward_references": {
                cls.klass.__name__: cls.klass,  # type: ignore
            },
        }

        if dacite_user_config is not None:
            dacite_config.update(dacite_user_config)

        return dacite_config

    @classmethod
    def fake(cls: Type[CT], **data: Dict[str, Any]) -> CT:
        """
        Creates a fake instance of the model.

        Attributes:
            data: Dict[str, Any] represent the user values to use in the instance
        """
        # only generate fakes for fields that were not provided in data
        payload = {field.name: field.fake() for field in cls.get_fields() if field.name not in data.keys()}
        payload.update(data)

        return from_dict(data_class=cls, data=payload, config=Config(**cls.config()))
