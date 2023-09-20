import pydantic

from . import fields

PYDANTIC_INMUTABLE_FIELDS_CLASSES = {
    pydantic.FilePath: fields.FilePathField,
    pydantic.DirectoryPath: fields.DirectoryPathField,
    pydantic.EmailStr: fields.EmailStrField,
    pydantic.NameEmail: fields.NameEmailField,
    pydantic.AnyUrl: fields.AnyUrlField,
    pydantic.AnyHttpUrl: fields.AnyHttpUrlField,
    pydantic.HttpUrl: fields.HttpUrlField,
    pydantic.FileUrl: fields.FileUrlField,
    pydantic.PostgresDsn: fields.PostgresDsnField,
    pydantic.CockroachDsn: fields.CockroachDsnField,
    pydantic.AmqpDsn: fields.AmqpDsnField,
    pydantic.RedisDsn: fields.RedisDsnField,
    pydantic.MongoDsn: fields.MongoDsnField,
    pydantic.KafkaDsn: fields.KafkaDsnField,
    pydantic.SecretStr: fields.SecretStrField,
    pydantic.IPvAnyAddress: fields.IPvAnyAddressField,
    pydantic.IPvAnyInterface: fields.IPvAnyInterfaceField,
    pydantic.IPvAnyNetwork: fields.IPvAnyNetworkField,
    pydantic.NegativeFloat: fields.NegativeFloatField,
    pydantic.PositiveFloat: fields.PositiveFloatField,
    pydantic.NegativeInt: fields.NegativeIntField,
    pydantic.PositiveInt: fields.PositiveIntField,
    pydantic.ConstrainedInt: fields.ConstrainedIntField,
    # ConstrainedIntValue is a dynamic type that needs to be referenced by qualified name
    # and cannot be imported directly
    "ConstrainedIntValue": fields.ConstrainedIntField,
}

PYDANTIC_LOGICAL_TYPES_FIELDS_CLASSES = {
    pydantic.UUID1: fields.UUID1Field,
    pydantic.UUID3: fields.UUID3Field,
    pydantic.UUID4: fields.UUID4Field,
    pydantic.UUID5: fields.UUID5Field,
}
