import dataclasses
import enum
import inspect
import json
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, TypeVar, Union

from dacite import Config, from_dict
from fastavro.validation import validate

from . import case, serialization
from .fields.base import Field
from .fields.fields import LiteralField
from .parser import Parser
from .types import JsonDict
from .utils import SchemaMetadata, standardize_custom_type

AVRO = "avro"
AVRO_JSON = "avro-json"


CT = TypeVar("CT", bound="AvroModel")


class AvroModel:
    _parser: Optional[Parser] = None
    _klass: Optional[Type] = None
    _metadata: Optional[SchemaMetadata] = None
    _user_defined_types: Set = set()
    _parent: Any = None
    _rendered_schema: OrderedDict = dataclasses.field(default_factory=OrderedDict)
    _field_type_hooks: Optional[Dict[Any, Callable[[Any], Any]]] = None

    @classmethod
    def generate_dataclass(cls: Type[CT]) -> Type[CT]:
        if dataclasses.is_dataclass(cls):
            return cls  # type: ignore
        return dataclasses.dataclass(cls)

    @classmethod
    def generate_metadata(cls: Type[CT]) -> SchemaMetadata:
        meta = getattr(cls._klass, "Meta", type)

        return SchemaMetadata.create(meta)

    @classmethod
    def generate_schema(cls: Type[CT], schema_type: str = "avro") -> Optional[OrderedDict]:
        if cls._parser is None or cls.__mro__[1] != AvroModel:
            # Generate dataclass and metadata
            cls._klass = cls.generate_dataclass()

            # let's live open the possibility to define different
            # schema definitions like json
            if schema_type == "avro":
                # cache the schema
                cls._parser = cls._generate_parser()
                cls._rendered_schema = cls._parser.render()
            else:
                raise ValueError("Invalid type. Expected avro schema type.")

        return cls._rendered_schema

    @classmethod
    def _generate_parser(cls: Type[CT]) -> Parser:
        cls._metadata = cls.generate_metadata()
        return Parser(type=cls._klass, metadata=cls._metadata, parent=cls._parent or cls)

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
            cls._parent = parent
            cls._parser = None
        else:
            # This happens when an AvroModel is the root of the tree (first class in the hierarchy)
            # Because intermediate schemas can be reused as a root later, we need to reset them
            # Example with A as a root:
            #     A -> B -> C -> D
            #
            # After generating the A.avro_schema the parent of B is A,
            # if we want to do B.avro_schema (now B is the root)
            # B should clean the data that was only valid when it was the child
            cls._reset_parser()

        avro_schema = cls.generate_schema(schema_type=AVRO)

        if case_type is not None:
            avro_schema = case.case_record(cls._rendered_schema, case_type)  # type: ignore

        return json.loads(json.dumps(avro_schema))

    @classmethod
    def get_fields(cls: Type[CT]) -> List[Field]:
        if cls._parser is None:
            cls.generate_schema()
        return cls._parser.fields  # type: ignore

    @classmethod
    def _reset_parser(cls: Type[CT]) -> None:
        """
        Reset all the values to original state.
        """
        cls._user_defined_types = set()
        cls._parser = None
        cls._parent = None

    def asdict(self, standardize_factory: Optional[Callable[..., Any]] = None) -> JsonDict:
        if standardize_factory is not None:
            return dataclasses.asdict(self, dict_factory=lambda x: {key: standardize_factory(value) for key, value in x})  # type: ignore
        return dataclasses.asdict(self)  # type: ignore

    def serialize(self, serialization_type: str = AVRO) -> bytes:
        schema = self.avro_schema_to_python()

        return serialization.serialize(
            self.asdict(standardize_factory=standardize_custom_type),
            schema,
            serialization_type=serialization_type,
        )

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
        obj = cls.parse_obj(payload)

        if not create_instance:
            return obj.asdict()
        return obj

    @classmethod
    def parse_obj(cls: Type[CT], data: Dict) -> CT:
        return from_dict(data_class=cls, data=data, config=cls.config())

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
    def get_field_type_hooks(cls: Type[CT]) -> Dict[Any, Callable[[Any], Any]]:
        """
        Workaround until dacite.from_dict supports fields of type
        Literal[enum.Enum]
        """
        if not cls._field_type_hooks:
            field_type_hooks: Dict[Any, Callable[[Any], Any]] = {}

            def populate_hooks(model: Type[AvroModel], _field_type_hooks: dict) -> None:
                fields_schema_map = model._parser.get_fields_map()  # type: ignore

                for field in fields_schema_map.values():
                    if isinstance(field, LiteralField):
                        _field_type_hooks[field.type] = field.get_dacite_typehook_transformer()
                    elif inspect.isclass(field.type) and issubclass(field.type, AvroModel):
                        # This field is a nested AvroModel, so recurse
                        populate_hooks(field.type, _field_type_hooks)

            populate_hooks(cls, field_type_hooks)
            cls._field_type_hooks = field_type_hooks

        return cls._field_type_hooks

    @classmethod
    def config(cls: Type[CT]) -> Config:
        """
        Get the default config for dacite and always include the self reference
        """
        # We need to make sure that the `avro schemas` has been generated, otherwise cls._klass is empty
        # It won't affect the performance because the rendered schema will be store in cls._rendered_schema
        cls.generate_schema()
        dacite_user_config = cls._metadata.dacite_config  # type: ignore

        dacite_config = {
            "check_types": False,
            "cast": [],
            "forward_references": {
                cls._klass.__name__: cls._klass,  # type: ignore
            },
            "type_hooks": cls.get_field_type_hooks(),
        }

        if dacite_user_config is not None:
            dacite_config.update(dacite_user_config)

        config = Config(**dacite_config)  # type: ignore

        # we always need to have this values regardless
        # the user config
        config.cast.extend([Tuple, tuple, enum.Enum])  # type: ignore
        return config

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

        return from_dict(data_class=cls, data=payload, config=cls.config())
