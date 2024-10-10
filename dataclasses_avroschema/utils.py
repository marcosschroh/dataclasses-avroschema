import dataclasses
import enum
import typing
from datetime import datetime, timezone
from functools import lru_cache

from typing_extensions import Annotated, get_origin

from .types import FieldInfo, JsonDict, UnionType

if typing.TYPE_CHECKING:
    from .main import AvroModel  # pragma: no cover
 
try:
    import pydantic  # pragma: no cover
    from pydantic import v1
except ImportError:  # type: ignore # pragma: no cover
    pydantic = None  # type: ignore # pragma: no cover


try:
    import faust  # pragma: no cover
except ImportError:  # type: ignore # pragma: no cover
    faust = None  # type: ignore # pragma: no cover


@lru_cache(maxsize=None)
def is_pydantic_model(klass: typing.Type) -> bool:
    if pydantic is not None:
        return issubclass(klass, v1.BaseModel) or issubclass(klass, pydantic.BaseModel)
    return False


@lru_cache(maxsize=None)
def is_faust_record(klass: typing.Type) -> bool:
    if faust is not None:
        return issubclass(klass, faust.Record)
    return False


def is_union(a_type: typing.Type) -> bool:
    """
    Given a python type, return True if is typing.Union, otherwise False

    Arguments:
        a_type (typing.Any): python type

    Returns:
        bool
    """
    if UnionType is None:
        return (
            isinstance(a_type, typing._GenericAlias) and a_type.__origin__ is typing.Union  # type: ignore
        )
    return (
        isinstance(a_type, typing._GenericAlias) and a_type.__origin__ is typing.Union or isinstance(a_type, UnionType)  # type: ignore
    )


def is_self_referenced(a_type: typing.Type, parent: typing.Type) -> bool:
    """
    Given a python type, return True if is self referenced, meaning
    that is instance of typing.ForwardRef, otherwise False

    Arguments:
        a_type (typing.Any): python type
        parent (typing.Any) python type

    Returns:
        bool

    Example:
        class User(...)
            a_type_with_type: typing.Type["User"]] = None
            a_type: "User" = None

        is_self_referenced(a_type) # True
    """
    return (
        isinstance(a_type, typing._GenericAlias)  # type: ignore
        and a_type.__args__
        and isinstance(a_type.__args__[0], typing.ForwardRef)
    ) or a_type == parent


def is_annotated(a_type: typing.Type) -> bool:
    origin = get_origin(a_type)
    return origin is not None and isinstance(origin, type) and issubclass(origin, Annotated)  # type: ignore[arg-type]


def rebuild_annotation(a_type: typing.Type, field_info: FieldInfo) -> typing.Type:
    return Annotated[a_type, field_info]  # type: ignore[return-value]


def standardize_custom_type(
    *,
    field_name: str,
    value: typing.Any,
    model: "AvroModel",
    base_class: typing.Type["AvroModel"],
    include_type: bool = True,
) -> typing.Any:
    if isinstance(value, dict):
        return {
            k: standardize_custom_type(field_name=field_name, value=v, model=model, base_class=base_class)
            for k, v in value.items()
        }
    elif isinstance(value, list):
        return [
            standardize_custom_type(field_name=field_name, value=v, model=model, base_class=base_class) for v in value
        ]
    elif isinstance(value, tuple):
        return tuple(
            standardize_custom_type(field_name=field_name, value=v, model=model, base_class=base_class) for v in value
        )
    elif isinstance(value, enum.Enum):
        return value.value
    elif isinstance(value, base_class):
        if is_faust_record(type(value)):  # type: ignore[arg-type]
            # we need to do a trick because we can not overrride asdict from faust..
            # once the function interface is introduced we can remove this check
            asdict = value.standardize_type()  # type: ignore
        else:
            asdict = value.asdict()

        if is_union(model.__annotations__[field_name]) and include_type:
            asdict["-type"] = value.get_fullname()
        return asdict

    return value


@dataclasses.dataclass
class SchemaMetadata:
    schema_name: typing.Optional[str] = None
    schema_doc: typing.Union[bool, str] = True
    namespace: typing.Optional[str] = None
    aliases: typing.Optional[typing.List[str]] = None
    alias_nested_items: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    dacite_config: typing.Optional[JsonDict] = None
    field_order: typing.Optional[typing.List[str]] = None
    exclude: typing.List[str] = dataclasses.field(default_factory=list)
    convert_literal_to_enum: bool = False

    @classmethod
    def create(cls: typing.Type["SchemaMetadata"], klass: type) -> "SchemaMetadata":
        return cls(
            schema_name=getattr(klass, "schema_name", None),
            schema_doc=getattr(klass, "schema_doc", True),
            namespace=getattr(klass, "namespace", None),
            aliases=getattr(klass, "aliases", None),
            alias_nested_items=getattr(klass, "alias_nested_items", {}),
            dacite_config=getattr(klass, "dacite_config", None),
            field_order=getattr(klass, "field_order", None),
            exclude=getattr(klass, "exclude", []),
            convert_literal_to_enum=getattr(klass, "convert_literal_to_enum", False),
        )

    def get_alias_nested_items(self, name: str) -> typing.Optional[str]:
        return self.alias_nested_items.get(name)


@dataclasses.dataclass
class FieldMetadata:
    default: typing.Any
    aliases: typing.List[str] = dataclasses.field(default_factory=list)
    doc: typing.Optional[str] = None
    namespace: typing.Optional[str] = None
    schema_name: typing.Optional[str] = None

    @classmethod
    def create(cls: typing.Type["FieldMetadata"], klass: typing.Optional[type]) -> "FieldMetadata":
        return cls(
            aliases=getattr(klass, "aliases", []),
            doc=getattr(klass, "doc", None),
            namespace=getattr(klass, "namespace", None),
            default=getattr(klass, "default", dataclasses.MISSING),
            schema_name=getattr(klass, "schema_name", None),
        )

    def to_dict(self) -> typing.Dict[str, typing.Union[typing.List[str], str]]:
        dict_repr = {key: value for key, value in vars(self).items() if value and key != "default"}

        if self.default is not dataclasses.MISSING:
            dict_repr["default"] = self.default

        return dict_repr


class UserDefinedType(typing.NamedTuple):
    name: str
    model: typing.Type


epoch: datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
epoch_naive: datetime = datetime(1970, 1, 1)
