from typing import Type, TypeVar

from fastavro.validation import validate

from dataclasses_avroschema.schema_generator import AvroModel

from .parser import FaustParser

try:
    from faust import Record  # pragma: no cover
except ImportError as ex:  # pragma: no cover
    raise Exception("faust-streaming must be installed in order to use AvroRecord") from ex  # pragma: no cover


CT = TypeVar("CT", bound="AvroRecord")


class AvroRecord(Record, AvroModel):  # type: ignore
    def validate_avro(self) -> bool:
        """
        Validate that instance matches the avro schema
        """
        schema = self.avro_schema_to_python()
        return validate(self.asdict(), schema)

    @classmethod
    def _generate_parser(cls: Type[CT]) -> FaustParser:
        cls._metadata = cls.generate_metadata()
        return FaustParser(type=cls._klass, metadata=cls._metadata, parent=cls._parent or cls)
