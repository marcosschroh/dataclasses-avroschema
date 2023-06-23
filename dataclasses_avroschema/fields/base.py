import abc
import dataclasses
import json
import logging
import typing
from collections import OrderedDict

from inflector import Inflector
from typing_extensions import get_args

from dataclasses_avroschema import utils

p = Inflector()

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
    default: typing.Any
    parent: typing.Any
    metadata: typing.Optional[typing.Mapping] = None
    model_metadata: typing.Optional[utils.SchemaMetadata] = None

    def __post_init__(self) -> None:
        self.model_metadata = self.model_metadata or utils.SchemaMetadata()  # type: ignore

    @property
    def avro_type(self) -> typing.Union[str, typing.Dict]:
        ...  # pragma: no cover

    @staticmethod
    def _get_self_reference_type(a_type: typing.Any) -> str:
        internal_type = a_type.__args__[0]

        return internal_type.__forward_arg__

    @staticmethod
    def get_singular_name(name: str) -> str:
        return p.singularize(name)

    def get_metadata(self) -> typing.List[typing.Tuple[str, str]]:
        meta_data_for_template = []

        if self.metadata is not None:
            try:
                for name, value in self.metadata.items():
                    meta_data_for_template.append((name, value))
            except (ValueError, TypeError):  # pragma: no cover
                logger.warn("Error during getting metadata")  # pragma: no cover
        return meta_data_for_template

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
            template["default"] = default

        return template

    def get_default_value(self) -> typing.Any:
        if self.default in (dataclasses.MISSING, None):
            return self.default
        else:
            self.validate_default()
            return self.default

    def validate_default(self) -> bool:
        a_type = self.type
        msg = f"Invalid default type. Default should be {self.type}"
        if utils.is_annotated(self.type):
            a_type, _ = get_args(self.type)

        assert isinstance(self.default, a_type), msg
        return True

    def to_json(self) -> str:
        return json.dumps(self.render(), indent=2)

    def to_dict(self) -> dict:
        return json.loads(self.to_json())

    @abc.abstractmethod
    def get_avro_type(self) -> typing.Any:
        ...  # pragma: no cover

    def fake(self) -> typing.Any:
        return None

    def exist_type(self) -> int:
        # filter by the same field types
        same_types = [
            field.type
            for field in self.parent.user_defined_types
            if field.type == self.type and field.name != self.name
        ]

        # If length > 0, means that it is the first appearance
        # of this type, otherwise exist already.
        return len(same_types)
