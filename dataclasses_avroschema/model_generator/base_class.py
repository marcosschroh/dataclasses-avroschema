import enum


class BaseClassEnum(str, enum.Enum):
    AVRO_MODEL = "AvroModel"
    PYDANTIC_MODEL = "BaseModel"
    AVRO_DANTIC_MODEL = "AvroBaseModel"
