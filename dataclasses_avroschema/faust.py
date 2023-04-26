from fastavro.validation import validate

from .schema_generator import AvroModel

try:
    from faust import Record  # pragma: no cover
except ImportError as ex:  # pragma: no cover
    raise Exception("faust-streaming must be installed in order to use AvroRecord") from ex  # pragma: no cover


class AvroRecord(Record, AvroModel):  # type: ignore
    def validate_avro(self) -> bool:
        """
        Validate that instance matches the avro schema
        """
        schema = self.avro_schema_to_python()
        return validate(self.asdict(), schema)
