import dataclasses
import inspect
import json
from collections import OrderedDict
from typing import Any, Dict, List, Literal, Optional, Set, Type, TypeVar, Union, overload

from dacite import Config, from_dict
from fastavro.validation import validate

from . import case, serialization
from .dacite_config import generate_dacite_config
from .fields.base import Field
from .parser import Parser
from .types import JsonDict
from .utils import UserDefinedType, standardize_custom_type

_schemas_cache: Dict["Type[AvroModel]", dict] = {}
_dacite_config_cache: Dict["Type[AvroModel]", Config] = {}
TSelf = TypeVar("TSelf", bound="AvroModel")


class AvroModel:
    _parser: Optional[Parser] = None
    _parent: Optional[Type["AvroModel"]] = None
    _user_defined_types: Set[UserDefinedType] = set()
    _rendered_schema: OrderedDict = dataclasses.field(default_factory=OrderedDict)

    @classmethod
    def get_fullname(cls: Type["AvroModel"]) -> str:
        """
        Fullname is composed of two parts: a name and a namespace
        separated by a dot. A namespace is a dot-separated sequence of such names.
        The empty string may also be used as a namespace to indicate the null namespace.
        Equality of names (including field names and enum symbols)
        as well as fullnames is case-sensitive.
        """
        # we need to make sure that the schema has been generated
        cls.generate_schema()
        assert cls._parser
        metadata = cls._parser.metadata

        if metadata.namespace:
            # if the current record has a namespace we use it
            return f"{metadata.namespace}.{cls.__name__}"
        elif cls._parent is not None:
            # if the record has a parent then we try to use the parent namespace
            assert cls._parent._parser
            parent_metadata = cls._parent._parser.metadata
            if parent_metadata.namespace:
                return f"{parent_metadata.namespace}.{cls.__name__}"
        return cls.__name__

    @classmethod
    def generate_schema(
        cls: Type["AvroModel"], schema_type: serialization.SerializationType = "avro"
    ) -> Optional[OrderedDict]:
        if cls._parser is None:
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
    def _get_serialization_context(cls) -> JsonDict:
        """
        Returns:
            Dict[str, Any] with the necesary context for the serialization/deserialization process
            It contains at least all the AvroModel defined by the end users represented by
            AvroModel.__name__: AvroModel entries
        """
        return {user_type.model.__name__: user_type.model for user_type in cls._user_defined_types}

    @classmethod
    def _generate_parser(cls: Type["AvroModel"]) -> Parser:
        return Parser(type=cls, parent=cls._parent or cls)

    @classmethod
    def avro_schema(cls: Type["AvroModel"], case_type: Optional[str] = None, **kwargs) -> str:
        return json.dumps(cls.avro_schema_to_python(case_type=case_type), **kwargs)

    @classmethod
    def avro_schema_to_python(
        cls: Type["AvroModel"],
        parent: Optional[Type["AvroModel"]] = None,
        case_type: Optional[str] = None,
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

        avro_schema = cls.generate_schema()

        if case_type is not None:
            avro_schema = case.case_record(cls._rendered_schema, case_type)  # type: ignore

        return json.loads(json.dumps(avro_schema))

    @classmethod
    def get_fields(cls: Type["AvroModel"]) -> List[Field]:
        if cls._parser is None:
            cls.generate_schema()
        return cls._parser.fields  # type: ignore

    @classmethod
    def _reset_parser(cls: Type["AvroModel"]) -> None:
        """
        Reset all the values to original state.
        """
        cls._user_defined_types = set()
        cls._parser = None
        cls._parent = None

    @classmethod
    @overload
    def deserialize(
        cls: Type[TSelf],
        data: bytes,
        serialization_type: serialization.SerializationType = ...,
        create_instance: Literal[True] = ...,
        writer_schema: Optional[Union[JsonDict, Type["AvroModel"]]] = ...,
    ) -> TSelf: ...
    @classmethod
    @overload
    def deserialize(
        cls: Type[TSelf],
        data: bytes,
        serialization_type: serialization.SerializationType = ...,
        create_instance: Literal[False] = ...,
        writer_schema: Optional[Union[JsonDict, Type["AvroModel"]]] = ...,
    ) -> JsonDict: ...
    @classmethod
    @overload
    def deserialize(
        cls: Type[TSelf],
        data: bytes,
        serialization_type: serialization.SerializationType = ...,
        create_instance: bool = ...,
        writer_schema: Optional[Union[JsonDict, Type["AvroModel"]]] = ...,
    ) -> Union[TSelf, JsonDict]: ...
    @classmethod
    def deserialize(
        cls,
        data,
        serialization_type="avro",
        create_instance=True,
        writer_schema=None,
    ):
        payload = cls.deserialize_to_python(data, serialization_type, writer_schema)
        obj = cls.parse_obj(payload)

        if not create_instance:
            return obj.to_dict()
        return obj

    @classmethod
    def deserialize_to_python(  # This can be used straight with a pydantic dataclass to bypass dacite
        cls: Type["AvroModel"],
        data: bytes,
        serialization_type: serialization.SerializationType = "avro",
        writer_schema: Union[JsonDict, Type["AvroModel"], None] = None,
    ) -> dict:
        if inspect.isclass(writer_schema) and issubclass(writer_schema, AvroModel):
            # mypy does not understand redefinitions
            writer_schema: JsonDict = writer_schema.avro_schema_to_python()  # type: ignore

        schema = _schemas_cache.get(cls)
        if schema is None:
            schema = cls.avro_schema_to_python()
            _schemas_cache[cls] = schema
        return serialization.deserialize(
            data=data,
            schema=schema,
            serialization_type=serialization_type,
            context=cls._get_serialization_context(),
            writer_schema=writer_schema,  # type: ignore
        )

    @classmethod
    def parse_obj(cls: Type[TSelf], data: Dict) -> TSelf:
        config = _dacite_config_cache.get(cls)
        if config is None:
            config = generate_dacite_config(cls)
            _dacite_config_cache[cls] = config
        return from_dict(data_class=cls, data=data, config=config)

    @classmethod
    def fake(cls: Type["AvroModel"], **data: Any) -> "AvroModel":
        """
        Creates a fake instance of the model.

        Keyword Arguments:
            Any user values to use in the instance. All fields not explicitly passed
            will be filled with fake data.
        """
        # only generate fakes for fields that were not provided in data
        payload = {field.name: field.fake() for field in cls.get_fields() if field.name not in data.keys()}
        payload.update(data)

        return from_dict(data_class=cls, data=payload, config=generate_dacite_config(cls))

    def asdict(self, include_type: bool = True) -> JsonDict:
        return {
            field.name: standardize_custom_type(
                field_name=field.name, value=getattr(self, field.name), model=self, base_class=AvroModel, include_type=include_type
            )
            for field in dataclasses.fields(self)  # type: ignore[arg-type]
        }

    def serialize(self, serialization_type: serialization.SerializationType = "avro") -> bytes:
        klass = type(self)
        schema = _schemas_cache.get(klass)
        if schema is None:
            schema = self.avro_schema_to_python()
            _schemas_cache[klass] = schema

        return serialization.serialize(
            self.asdict(),
            schema,
            serialization_type=serialization_type,
        )

    def validate(self) -> bool:
        schema = self.avro_schema_to_python()
        return validate(self.asdict(), schema)

    def to_dict(self) -> JsonDict:
        return dataclasses.asdict(self)  # type: ignore

    def to_json(self, **kwargs: Any) -> str:
        data = serialization.to_json(self.to_dict())
        return json.dumps(data, **kwargs)
