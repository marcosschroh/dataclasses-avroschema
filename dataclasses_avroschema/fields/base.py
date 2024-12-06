import abc
import dataclasses
import json
import logging
import typing
from collections import OrderedDict

import inflection
from typing_extensions import get_args

from dataclasses_avroschema import utils

logger = logging.getLogger(__name__)


@dataclasses.dataclass  # type: ignore
class Field:
    __slots__ = (
        "name",
        "type",
        "default",
        "parent",
    )

    name: str
    type: typing.Any  # store the python primitive type
    parent: typing.Any
    default: typing.Any
    default_factory: typing.Any = dataclasses.MISSING
    exclude_default: bool = False
    inner_name: typing.Optional[str] = None
    metadata: typing.Dict = dataclasses.field(default_factory=dict)
    model_metadata: utils.SchemaMetadata = dataclasses.field(default_factory=utils.SchemaMetadata)
    extra_default_types_allowed: typing.Tuple = dataclasses.field(default_factory=tuple)
    # This is the metadata that the end user has defined in the dataclasses.Field or pydantic.Field
    metadata_to_exclude: typing.List[str] = dataclasses.field(
        default_factory=lambda: [
            "exclude_default",
            "inner_name",
        ]
    )

    def __post_init__(self) -> None:
        self.exclude_default = self.metadata.get("exclude_default", False)  # type: ignore
        self.inner_name = self.metadata.get("inner_name", None)  # type: ignore

    @property
    def avro_type(self) -> typing.Union[str, typing.Dict]:  # type: ignore
        ...  #  pragma: no cover

    @staticmethod
    def _get_self_reference_type(a_type: typing.Any) -> str:
        if getattr(a_type, "__args__", None):
            internal_type = a_type.__args__[0]
            return internal_type.__forward_arg__
        return a_type.__name__

    @staticmethod
    def get_singular_name(name: str) -> str:
        return inflection.singularize(name)

    def get_metadata(self) -> typing.List[typing.Tuple[str, str]]:
        return [(name, value) for name, value in self.metadata.items() if name not in self.metadata_to_exclude]

    def render(self) -> OrderedDict:
        """
        Render the fields base on the avro field

        At least will have name and type.

        returns:
            OrderedDict(
                ("name", "a name"),
                ("type", "a type"),
                ("default", "default value")
            )

            The default key is optional.

            If self.type is:
                * list, the OrderedDict will contains the key items inside type
                * tuple, he OrderedDict will contains the key symbols inside type
                * dict, he OrderedDict will contains the key values inside type
        """
        template = OrderedDict(self.get_metadata() + [("name", self.name), ("type", self.get_avro_type())])
        default = self.get_default_value()

        if default is not dataclasses.MISSING:
            if default is not None:
                self.validate_default(default)
                default = self.default_to_avro(default)

            template["default"] = default

        return template

    def get_default_value(self) -> typing.Any:
        if self.exclude_default:
            return dataclasses.MISSING

        is_default_factory_callable = callable(self.default_factory)

        if is_default_factory_callable:
            return self.default_factory()
        return self.default

    def validate_default(self, default: typing.Any) -> bool:
        a_type = (self.type, *self.extra_default_types_allowed)
        msg = f'Invalid default type {type(default)} for field "{self.name}". Default should be {self.type}'

        if utils.is_annotated(self.type):
            a_type, _ = get_args(self.type)

        assert isinstance(default, a_type), msg
        return True

    def default_to_avro(self, value: typing.Any) -> typing.Any:
        return value

    def to_json(self) -> str:
        return json.dumps(self.render(), indent=2)

    def to_dict(self) -> dict:
        return dict(self.render())

    @abc.abstractmethod
    def get_avro_type(self) -> typing.Any: ...  # pragma: no cover

    def fake(self) -> typing.Any:
        return None

    def exist_type(self) -> int:
        # filter by the same field types
        same_types = [field.model for field in self.parent._user_defined_types if field.model == self.type]

        # If length > 0, means that it is the first appearance
        # of this type, otherwise exist already.
        return len(same_types)
