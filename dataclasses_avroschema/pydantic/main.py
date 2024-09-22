import json
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from fastavro.validation import validate

from dataclasses_avroschema import serialization
from dataclasses_avroschema.schema_generator import AVRO, AvroModel
from dataclasses_avroschema.types import JsonDict
from dataclasses_avroschema.utils import standardize_custom_type

from .parser import PydanticParser

try:
    from pydantic import BaseModel  # pragma: no cover
except ImportError as ex:  # pragma: no cover
    raise Exception("pydantic must be installed in order to use AvroBaseModel") from ex  # pragma: no cover

CT = TypeVar("CT", bound="AvroBaseModel")


class AvroBaseModel(BaseModel, AvroModel):  # type: ignore
    @classmethod
    def model_dump(cls: Type[CT], *args: Any, **kwargs: Any) -> dict[str, Any]:
        data = cls.model_dump(*args, **kwargs)
        data["-type"] = cls.__name__
        return data

    @classmethod
    def generate_dataclass(cls: Type[CT]) -> Type[CT]:
        return cls

    @classmethod
    def json_schema(cls: Type[CT], *args: Any, **kwargs: Any) -> str:
        return json.dumps(cls.model_json_schema(*args, **kwargs))

    @classmethod
    def standardize_type(cls: Type[CT], data: dict) -> Any:
        """
        Standardization factory that converts data according to the
        user-defined pydantic json_encoders prior to passing values
        to the standard type conversion factory
        """
        for value in data.values():
            if isinstance(value, dict):
                cls.standardize_type(value)

        return standardize_custom_type(data)

    def asdict(self, standardize_factory: Optional[Callable[..., Any]] = None) -> JsonDict:
        """
        Returns this model in dictionary form. This method differs from
        pydantic's dict by converting all values to their Avro representation.
        It also doesn't provide the exclude, include, by_alias, etc.
        parameters that dict provides.
        """
        data = self.model_dump()
        standardize_method = standardize_factory or self.standardize_type

        # the standardize called can be replaced if we have a custom implementation of asdict
        # for now I think is better to use the native implementation
        return standardize_method(data)

    @classmethod
    def parse_obj(cls: Type[CT], data: Dict) -> CT:
        return cls.model_validate(obj=data)

    def serialize(self, serialization_type: str = AVRO) -> bytes:
        """
        Overrides the base AvroModel's serialize method to inject this
        class's standardization factory method
        """
        schema = self.avro_schema_to_python()

        return serialization.serialize(
            self.asdict(standardize_factory=self.standardize_type),
            schema,
            serialization_type=serialization_type,
        )

    def validate_avro(self) -> bool:
        """
        Validate that instance matches the avro schema
        """
        schema = self.avro_schema_to_python()
        return validate(self.asdict(), schema)

    @classmethod
    def fake(cls: Type[CT], **data: Any) -> CT:
        """
        Creates a fake instance of the model.

        Attributes:
            data: Dict[str, Any] represent the user values to use in the instance
        """
        # only generate fakes for fields that were not provided in data
        payload = {field.name: field.fake() for field in cls.get_fields() if field.name not in data.keys()}
        payload.update(data)

        return cls.model_validate(payload)

    @classmethod
    def _generate_parser(cls: Type[CT]) -> PydanticParser:
        cls._metadata = cls.generate_metadata()
        return PydanticParser(type=cls._klass, metadata=cls._metadata, parent=cls._parent or cls)
