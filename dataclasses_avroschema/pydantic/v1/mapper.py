from pydantic import v1

from dataclasses_avroschema.pydantic import fields

PYDANTIC_INMUTABLE_FIELDS_CLASSES = {
    v1.FilePath: fields.FilePathField,
    v1.DirectoryPath: fields.DirectoryPathField,
    v1.EmailStr: fields.EmailStrField,
    v1.NameEmail: fields.NameEmailField,
    v1.AnyUrl: fields.AnyUrlField,
    v1.AnyHttpUrl: fields.AnyHttpUrlField,
    v1.HttpUrl: fields.HttpUrlField,
    v1.FileUrl: fields.FileUrlField,
    v1.PostgresDsn: fields.PostgresDsnField,
    v1.CockroachDsn: fields.CockroachDsnField,
    v1.AmqpDsn: fields.AmqpDsnField,
    v1.RedisDsn: fields.RedisDsnField,
    v1.MongoDsn: fields.MongoDsnField,
    v1.KafkaDsn: fields.KafkaDsnField,
    v1.SecretStr: fields.SecretStrField,
    v1.IPvAnyAddress: fields.IPvAnyAddressField,
    v1.IPvAnyInterface: fields.IPvAnyInterfaceField,
    v1.IPvAnyNetwork: fields.IPvAnyNetworkField,
    v1.NegativeFloat: fields.NegativeFloatField,
    v1.PositiveFloat: fields.PositiveFloatField,
    v1.NegativeInt: fields.NegativeIntField,
    v1.PositiveInt: fields.PositiveIntField,
    v1.ConstrainedInt: fields.ConstrainedIntField,
    # ConstrainedIntValue is a dynamic type that needs to be referenced by qualified name
    # and cannot be imported directly
    "ConstrainedIntValue": fields.ConstrainedIntField,
}


PYDANTIC_LOGICAL_TYPES_FIELDS_CLASSES = {
    v1.UUID1: fields.UUID1Field,
    v1.UUID3: fields.UUID3Field,
    v1.UUID4: fields.UUID4Field,
    v1.UUID5: fields.UUID5Field,
}
