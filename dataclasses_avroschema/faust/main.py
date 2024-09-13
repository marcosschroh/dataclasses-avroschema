import typing

from fastavro.validation import validate

from dataclasses_avroschema import serialization
from dataclasses_avroschema.schema_generator import AVRO, AvroModel
from dataclasses_avroschema.types import JsonDict
from dataclasses_avroschema.utils import standardize_custom_type

from .parser import FaustParser

try:
    from faust import Record  # pragma: no cover
except ImportError as ex:  # pragma: no cover
    raise Exception("faust-streaming must be installed in order to use AvroRecord") from ex  # pragma: no cover


CT = typing.TypeVar("CT", bound="AvroRecord")


class AvroRecord(Record, AvroModel):  # type: ignore
    def validate_avro(self) -> bool:
        """
        Validate that instance matches the avro schema
        """
        schema = self.avro_schema_to_python()
        return validate(self.asdict(), schema)

    def standardize_type(self) -> typing.Any:
        """
        Standardization factory that converts data according to the
        user-defined pydantic json_encoders prior to passing values
        to the standard type conversion factory
        """
        return standardize_custom_type(self)

    def serialize(self, serialization_type: str = AVRO) -> bytes:
        """
        Overrides the base AvroModel's serialize method to inject this
        class's standardization factory method
        """
        schema = self.avro_schema_to_python()
        data = self.standardize_type()

        return serialization.serialize(
            data,
            schema,
            serialization_type=serialization_type,
        )

    @classmethod
    def deserialize(
        cls: typing.Type[CT],
        data: bytes,
        serialization_type: str = AVRO,
        create_instance: bool = True,
        writer_schema: typing.Optional[typing.Union[JsonDict, typing.Type[CT]]] = None,
    ) -> typing.Union[JsonDict, CT]:
        payload = cls.deserialize_to_python(data, serialization_type, writer_schema)
        obj = cls.parse_obj(payload)

        if not create_instance:
            return obj.standardize_type()
        return obj

    def to_dict(self) -> JsonDict:
        return self.standardize_type()

    @classmethod
    def _generate_parser(cls: typing.Type[CT]) -> FaustParser:
        cls._metadata = cls.generate_metadata()
        return FaustParser(type=cls._klass, metadata=cls._metadata, parent=cls._parent or cls)
