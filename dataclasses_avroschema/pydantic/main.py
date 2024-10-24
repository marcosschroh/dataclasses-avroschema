import json
from typing import Any, Dict, Type, TypeVar

from fastavro.validation import validate

from dataclasses_avroschema import AvroModel, CustomAvroEncoder, serialization
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
    def generate_dataclass(cls: Type[CT]) -> Type[CT]:
        return cls

    @classmethod
    def json_schema(cls: Type[CT], *args: Any, **kwargs: Any) -> str:
        return json.dumps(cls.model_json_schema(*args, **kwargs))

    def _standardize_type(self) -> Dict[str, Any]:
        """
        Standardization factory that converts data according to the
        user-defined avro encoders prior to passing values
        to the standard type conversion factory.

        If an Annotation-based custom encoder is found on a field, that
        encoder will be used, and no `json_encoders`-based encoders will be
        used, even if they exist.
        """

        data = dict(self)

        # Encoders are annotations on field types
        custom_encoders = {
            k: next((item for item in v.metadata if isinstance(item, CustomAvroEncoder)), None)
            for k, v in self.model_fields.items()
        }

        # Encoders are in deprecated pydantic `json_encoders` model config field
        json_encoders = self.model_config.get("json_encoders") or {}
        for k, v in data.items():
            v_type = type(v)
            custom_encoder = custom_encoders.get(k)
            json_encoder = json_encoders.get(v_type)
            if custom_encoder:
                data[k] = custom_encoder.to_avro(v)
            elif json_encoder:
                data[k] = json_encoder(v)

        return data

    def asdict(self) -> JsonDict:
        """
        Returns this model in dictionary form. This method differs from
        pydantic's dict by converting all values to their Avro representation.
        It also doesn't provide the exclude, include, by_alias, etc.
        parameters that dict provides.
        """
        return {
            field_name: standardize_custom_type(
                field_name=field_name, value=field_value, model=self, base_class=AvroBaseModel
            )
            for field_name, field_value in self._standardize_type().items()
        }

    @classmethod
    def parse_obj(cls: Type[CT], data: Dict) -> CT:
        return cls.model_validate(obj=data)

    def to_dict(self) -> JsonDict:
        return self.model_dump()

    def serialize(self, serialization_type: serialization.SerializationType = "avro") -> bytes:
        """
        Overrides the base AvroModel's serialize method to inject this
        class's standardization factory method
        """
        schema = self.avro_schema_to_python()

        return serialization.serialize(
            self.asdict(),
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
        return PydanticParser(type=cls._klass, metadata=cls.get_metadata(), parent=cls._parent or cls)
