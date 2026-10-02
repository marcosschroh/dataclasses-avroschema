import abc
import dataclasses
import typing
from collections import OrderedDict
from typing import Literal, overload

from .types import JsonDict, SerializationType
from .utils import (
    SchemaMetadata,
    UserDefinedType,
)

CT = typing.TypeVar("CT", bound="ModelProtocol")
# This means that when we have List[Protocol] can be use when we have List[ParserProtocol]
CP = typing.TypeVar("CP", bound="ParserProtocol", covariant=True)


class FieldProtocol(typing.Protocol):
    name: str
    type: typing.Any  # store the python primitive type
    parent: typing.Type["ModelProtocol"]
    default: typing.Any
    default_factory: typing.Any = dataclasses.MISSING
    exclude_default: bool = False
    inner_name: typing.Optional[str] = None
    metadata: typing.Dict = dataclasses.field(default_factory=dict)
    model_metadata: SchemaMetadata = dataclasses.field(default_factory=SchemaMetadata)
    extra_default_types_allowed: typing.Tuple = dataclasses.field(default_factory=tuple)
    # This is the metadata that the end user has defined in the dataclasses.Field or pydantic.Field
    metadata_to_exclude: typing.List[str] = dataclasses.field(
        default_factory=lambda: [
            "exclude_default",
            "inner_name",
        ]
    )

    def __init__(self, name: str, type: typing.Type, **kwargs: typing.Any): ...

    def __post_init__(self) -> None: ...

    @property
    def avro_type(self) -> typing.Union[str, typing.Dict]: ...

    @staticmethod
    def get_singular_name(name: str) -> str: ...

    @abc.abstractmethod
    def get_avro_type(self) -> typing.Union[str, JsonDict, typing.List]: ...  # pragma: no cover

    def get_default_value(self) -> typing.Any: ...

    def get_metadata(self) -> typing.List[typing.Tuple[str, str]]: ...

    def render(self) -> OrderedDict: ...

    def validate_default(self, default: typing.Any) -> bool: ...

    def default_to_avro(self, value: typing.Any) -> typing.Any: ...

    def to_json(self) -> str: ...

    def to_dict(self) -> dict: ...

    def fake(self) -> typing.Any: ...

    def exist_type(self) -> int: ...


class ParserProtocol(typing.Protocol[CP]):
    """
    Parse python dataclasses to represent it as an avro schema.

    Each classes field is converted into an AvroField in order to
    be represented as an avro type.
    """

    metadata: SchemaMetadata

    def __init__(self, type: typing.Type["ModelProtocol"], parent: typing.Type["ModelProtocol"]): ...

    def generate_dataclass(self) -> typing.Type: ...

    def parse_fields(self, exclude: typing.List) -> typing.List[FieldProtocol]: ...

    def get_fields_map(self) -> typing.Dict[str, FieldProtocol]: ...

    def get_schema_name(self) -> str: ...

    def generate_documentation(self) -> typing.Optional[str]: ...

    def get_rendered_fields(self) -> typing.List[OrderedDict]: ...

    def render(self) -> OrderedDict: ...


class ModelProtocol(typing.Protocol[CT]):
    _parser: typing.Optional[ParserProtocol] = None
    _parent: typing.Optional[CT] = None
    _user_defined_types: typing.Set[UserDefinedType] = set()
    _rendered_schema: OrderedDict = dataclasses.field(default_factory=OrderedDict)

    @classmethod
    def get_fullname(cls: typing.Type[CT]) -> str: ...

    @classmethod
    def generate_schema(
        cls: typing.Type[CT], schema_type: SerializationType = "avro"
    ) -> typing.Optional[OrderedDict]: ...

    @classmethod
    def _get_serialization_context(cls: typing.Type[CT]) -> JsonDict: ...

    @classmethod
    def _generate_parser(cls: typing.Type[CT]) -> ParserProtocol: ...

    @classmethod
    def avro_schema(cls: typing.Type[CT], case_type: typing.Optional[str] = None, **kwargs) -> str: ...

    @classmethod
    def avro_schema_to_python(
        cls: typing.Type[CT],
        parent: typing.Optional[CT] = None,
        case_type: typing.Optional[str] = None,
    ) -> typing.Dict[str, typing.Any]: ...

    @classmethod
    def get_fields(cls: typing.Type[CT]) -> typing.List[FieldProtocol]: ...

    @classmethod
    def _reset_parser(cls: typing.Type[CT]) -> None: ...

    @classmethod
    @overload
    def deserialize(
        cls: typing.Type[CT],
        data: bytes,
        serialization_type: SerializationType = "avro",
        create_instance: Literal[True] = ...,
        writer_schema: typing.Optional[typing.Union[JsonDict, typing.Type[CT]]] = None,
    ) -> CT: ...

    @classmethod
    @overload
    def deserialize(
        cls: typing.Type[CT],
        data: bytes,
        serialization_type: SerializationType = "avro",
        create_instance: Literal[False] = ...,
        writer_schema: typing.Optional[typing.Union[JsonDict, typing.Type[CT]]] = None,
    ) -> JsonDict: ...

    @classmethod
    @overload
    def deserialize(
        cls: typing.Type[CT],
        data: bytes,
        serialization_type: SerializationType = "avro",
        create_instance: bool = ...,
        writer_schema: typing.Optional[typing.Union[JsonDict, typing.Type[CT]]] = None,
    ) -> typing.Union[JsonDict, CT]: ...

    @classmethod
    def deserialize_to_python(  # This can be used straight with a pydantic dataclass to bypass dacite
        cls: typing.Type[CT],
        data: bytes,
        serialization_type: SerializationType = "avro",
        writer_schema: typing.Union[JsonDict, typing.Type[CT], None] = None,
    ) -> dict: ...

    @classmethod
    def parse_obj(cls: typing.Type[CT], data: typing.Dict) -> CT: ...

    @classmethod
    def fake(cls: typing.Type[CT], **data: typing.Any) -> CT: ...

    def asdict(self: CT) -> JsonDict: ...

    def serialize(self: CT, serialization_type: SerializationType = "avro") -> bytes: ...

    # def validate(self: CT) -> bool: ...

    def to_dict(self: CT) -> JsonDict: ...

    def to_json(self: CT, **kwargs: typing.Any) -> str: ...
