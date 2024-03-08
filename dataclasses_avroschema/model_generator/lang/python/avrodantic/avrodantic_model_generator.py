import typing
from dataclasses import dataclass

from dataclasses_avroschema.model_generator.lang.python import templates
from dataclasses_avroschema.model_generator.lang.python.base import BaseGenerator
from dataclasses_avroschema.types import JsonDict


@dataclass
class AvroDanticModelGenerator(BaseGenerator):
    def __post_init__(self) -> None:
        super().__post_init__()

        self.base_class = "AvroBaseModel"
        self.imports.add("from dataclasses_avroschema.pydantic import AvroBaseModel")
        self.imports_dict = {
            "dataclass_field": "from pydantic import Field",
        }

        # Templates
        self.field_template = templates.pydantic_field_template

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
            self.imports.add("import pydantic")
            return f"pydantic.{pydantic_class}"
        return None

    def render_dataclass_field(self, properties: str) -> str:
        self.imports.add("from pydantic import Field")
        return super().render_dataclass_field(properties=properties)
