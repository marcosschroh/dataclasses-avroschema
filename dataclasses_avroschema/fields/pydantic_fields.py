import typing
import uuid
from pathlib import Path

from dataclasses_avroschema.faker import fake

from . import fields
from .field_utils import DOUBLE, LONG, STRING, UUID

current_file = str(Path(__file__).absolute())
current_dir = str(Path().absolute())


class FilePathField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "FilePat"}

    def fake(self) -> str:
        return current_file


class DirectoryPathField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "DirectoryPath"}

    def fake(self) -> str:
        return current_dir


class EmailStrField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "EmailStr"}

    def fake(self) -> str:
        return fake.company_email()


class NameEmailField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "NameEmail"}

    def fake(self) -> str:
        first_name = fake.first_name()
        last_name = fake.last_name()

        return f"{first_name} {last_name} <{first_name}.{last_name}@example.com>"


class AnyUrlField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "AnyUrl"}

    def fake(self) -> str:
        return fake.url()


class AnyHttpUrlField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "AnyHttpUrl"}

    def fake(self) -> str:
        return fake.uri()


class HttpUrlField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "HttpUrl"}

    def fake(self) -> str:
        return fake.uri()


class FileUrlField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "FileUrl"}

    def fake(self) -> str:
        return f"file://{current_file}"


class PostgresDsnField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "PostgresDsn"}

    def fake(self) -> str:
        return f"postgres://{fake.first_name()}:{fake.pystr()}@127.0.0.1:5432/dummy"


class CockroachDsnField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "CockroachDsn"}

    def fake(self) -> str:
        return f"cockroachdb://{fake.first_name()}@127.0.0.1:26257/keto?sslmode=disable"


class AmqpDsnField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "AmqpDsn"}

    def fake(self) -> str:
        return f"amqp://{fake.first_name()}:{fake.pystr()}@25@myrabbitserver:5672/filestream"


class RedisDsnField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "RedisDsn"}

    def fake(self) -> str:
        return f"redis://{fake.first_name()}:{fake.pystr()}@localhost.com:6379"


class MongoDsnField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "MongoDsn"}

    def fake(self) -> str:
        return f"mongodb://{fake.first_name()}:{fake.pystr()}@mongodb0.example.com:27017"


class KafkaDsnField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "KafkaDsn"}

    def fake(self) -> str:
        return "kafka://9092"


class SecretStrField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "SecretStr"}

    def fake(self) -> str:
        return "**********"


class IPvAnyAddressField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "IPvAnyAddress"}

    def fake(self) -> str:
        return fake.ipv4()


class IPvAnyInterfaceField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "IPvAnyInterface"}

    def fake(self) -> str:
        return fake.ipv4()


class IPvAnyNetworkField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": STRING, "pydantic-class": "IPvAnyNetwork"}

    def fake(self) -> str:
        return fake.ipv4()


class NegativeFloatField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": DOUBLE, "pydantic-class": "NegativeFloat"}

    def fake(self) -> float:
        return fake.pyfloat(positive=False, max_value=0)


class PositiveFloatField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": DOUBLE, "pydantic-class": "PositiveFloat"}

    def fake(self) -> float:
        return fake.pyfloat(positive=True)


class NegativeIntField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": LONG, "pydantic-class": "NegativeInt"}

    def fake(self) -> int:
        return fake.pyint(max_value=0, min_value=-100)


class PositiveIntField(fields.ImmutableField):
    avro_type: typing.ClassVar[typing.Dict[str, str]] = {"type": LONG, "pydantic-class": "PositiveInt"}

    def fake(self) -> int:
        return fake.pyint(min_value=0)

    def validate_default(self) -> bool:
        return True


class UUID1Field(fields.UUIDField):
    @property
    def avro_type(self) -> typing.Dict:
        return {"type": STRING, "logicalType": UUID, "pydantic-class": "UUID1"}

    def fake(self) -> uuid.UUID:
        return uuid.uuid1()


class UUID3Field(fields.UUIDField):
    @property
    def avro_type(self) -> typing.Dict:
        return {"type": STRING, "logicalType": UUID, "pydantic-class": "UUID3"}

    def fake(self) -> uuid.UUID:
        return uuid.uuid3(namespace=uuid.NAMESPACE_URL, name=fake.pystr())


class UUID4Field(fields.UUIDField):
    @property
    def avro_type(self) -> typing.Dict:
        return {"type": STRING, "logicalType": UUID, "pydantic-class": "UUID4"}

    def fake(self) -> uuid.UUID:
        return uuid.uuid4()


class UUID5Field(fields.UUIDField):
    @property
    def avro_type(self) -> typing.Dict:
        return {"type": STRING, "logicalType": UUID, "pydantic-class": "UUID5"}

    def fake(self) -> uuid.UUID:
        return uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=fake.pystr())
