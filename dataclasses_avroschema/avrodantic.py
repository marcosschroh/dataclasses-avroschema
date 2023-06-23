from typing import Any, Callable, Optional, Type, TypeVar

from fastavro.validation import validate

from dataclasses_avroschema.schema_generator import AvroModel
from dataclasses_avroschema.types import JsonDict
from dataclasses_avroschema.utils import standardize_custom_type

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
        return cls.schema_json(*args, **kwargs)

    def asdict(self, standardize_factory: Optional[Callable[..., Any]] = None) -> JsonDict:
        """
        Document this. asdict vs dict
        """
        data = dict(self)

        standardize_method = standardize_factory or standardize_custom_type

        # te standardize called can be replaced if we have a custom implementation of asdict
        # for now I think is better to use the native implementation
        return standardize_method(data)

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

        return cls.parse_obj(payload)
