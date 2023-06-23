import pydantic

from dataclasses_avroschema.avrodantic import fields

PYDANTIC_INMUTABLE_FIELDS_CLASSES = {
    pydantic.FilePath: fields.FilePathField,
    # pydantic.DirectoryPath: fields.StringField,
    # pydantic.EmailStr: fields.StringField,
    # pydantic.NameEmail: fields.StringField,
    # pydantic.AnyUrl: fields.StringField,
    # pydantic.AnyHttpUrl: fields.StringField,
    # pydantic.HttpUrl: fields.StringField,
    # pydantic.FileUrl: fields.StringField,
    # pydantic.PostgresDsn: fields.StringField,
    # pydantic.CockroachDsn: fields.StringField,
    # pydantic.AmqpDsn: fields.StringField,
    # pydantic.RedisDsn: fields.StringField,
    # pydantic.MongoDsn: fields.StringField,
    # pydantic.KafkaDsn: fields.StringField,
    # pydantic.SecretStr: fields.StringField,
    # pydantic.IPvAnyAddress: fields.StringField,
    # pydantic.IPvAnyInterface: fields.StringField,
    # pydantic.IPvAnyNetwork: fields.StringField,
    # pydantic.NegativeFloat: fields.DoubleField,
    # pydantic.PositiveFloat: fields.DoubleField,
    # pydantic.NegativeInt: fields.LongField,
    # pydantic.PositiveInt: fields.LongField,
}


PYDANTIC_CONTAINER_FIELDS_CLASSES = {
    # pydantic.Json: fields.DictField,
}

PYDANTIC_LOGICAL_TYPES_FIELDS_CLASSES = {
    # pydantic.UUID1: fields.UUIDField,
    # pydantic.UUID3: fields.UUIDField,
    # pydantic.UUID4: fields.UUIDField,
    # pydantic.UUID5: fields.UUIDField,
}
