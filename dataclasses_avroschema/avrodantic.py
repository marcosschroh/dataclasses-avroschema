from typing import Any, Dict, Type, TypeVar

from fastavro.validation import validate

from .schema_generator import AvroModel, JsonDict

try:
    from pydantic import BaseModel  # pragma: no cover
except ImportError as ex:  # pragma: no cover
    raise Exception("pydantic must be installed in order to use AvroBaseModel") from ex  # pragma: no cover

CT = TypeVar("CT", bound="AvroBaseModel")


class AvroBaseModel(BaseModel, AvroModel):  # type: ignore
    @classmethod
    def json_schema(cls: Type[CT], *args: Any, **kwargs: Any) -> str:
        return cls.schema_json(*args, **kwargs)

    def asdict(self) -> JsonDict:
        """
        Document this. asdict vs dict
        """
        data = self.dict()

        # te standardize called can be replaced if we have a custom implementation of asdict
        # for now I think is better to use the native implementation
        return {key: self.standardize_custom_type(value) for key, value in data.items()}

    def validate_avro(self) -> bool:
        """
        Document this!!!
        """
        schema = self.avro_schema_to_python()
        return validate(self.asdict(), schema)

    @classmethod
    def parse_obj(cls: Type["AvroBaseModel"], data: Dict) -> "AvroBaseModel":
        return super().parse_obj(data)

    @classmethod
    def fake(cls: Type[CT], **data: Dict[str, Any]) -> "AvroBaseModel":
        """
        Creates a fake instance of the model.

        Attributes:
            data: Dict[str, Any] represent the user values to use in the instance
        """
        # only generate fakes for fields that were not provided in data
        payload = {field.name: field.fake() for field in cls.get_fields() if field.name not in data.keys()}
        payload.update(data)

        return cls.parse_obj(payload)
