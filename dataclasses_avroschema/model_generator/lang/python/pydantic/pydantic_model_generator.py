import typing
from dataclasses import MISSING, dataclass

from dataclasses_avroschema.model_generator.lang.python import templates
from dataclasses_avroschema.model_generator.lang.python.base import BaseGenerator, FieldRepresentation
from dataclasses_avroschema.types import JsonDict


@dataclass
class PydanticFieldRepresentation(FieldRepresentation):
    def get_field_metadata(self) -> typing.Optional[str]:
        metadata = {k: v for k, v in self.metadata.items() if k != "doc"}
        if metadata:
            return f"metadata={metadata}"
        return None

    def add_field_properties(self, default_repr: str) -> str:
        field_metadata_repr = self.get_field_metadata()

        if "doc" in self.metadata:
            doc = self.metadata["doc"]
            description = f'description="{doc}"'

            if field_metadata_repr:
                field_metadata_repr = f"{field_metadata_repr}, {description}"
            else:
                field_metadata_repr = description

        if field_metadata_repr or isinstance(self.default, (dict, list)):
            dataclass_field_properties = [field_metadata_repr]

            if isinstance(self.default, (dict, list)):
                if self.default:
                    dataclass_prop = f"default_factory=lambda: {default_repr}"
                else:
                    dataclass_prop = f"default_factory={default_repr}"

                dataclass_field_properties.append(dataclass_prop)
            else:
                if self.default is not MISSING:
                    dataclass_field_properties.append(f"default={default_repr}")

            default_repr = self.render_dataclass_field(
                properties=", ".join([prop for prop in dataclass_field_properties if prop])
            )

        return default_repr


@dataclass
class PydanticModelGenerator(BaseGenerator):
    def __post_init__(self) -> None:
        super().__post_init__()

        self.base_class = "pydantic.BaseModel"
        self.imports_dict = {
            "dataclass_field": "from pydantic import Field",
        }

        # Templates
        self.field_template = templates.pydantic_field_template
        self.field_representation_class = PydanticFieldRepresentation

    def _resolve_type_from_metadata(self, *, field: JsonDict) -> typing.Optional[str]:
        """
        Check if the language type must be replaced with any extra class which
        was specified in the field metadata. This method should be only called
        after the native type was resolved properly.

        An example of this if when a pydantic field was used in the model:

        class MyModel(AvroBaseModel):
            email: pydantic.EmailStr

        then the email field is represented as:

        {"name": "email", "type": {"type": "string", "pydantic-class": "EmailStr"}}

        For now we only recognize the attribute `pydantic-class` but in the future
        new way might be added, for example: `java-class`.

        """
        pydantic_class = field.get("pydantic-class")

        if pydantic_class is not None:
            return f"pydantic.{pydantic_class}"
        return None

    def add_class_imports(self) -> None:
        self.imports.add("import pydantic")
