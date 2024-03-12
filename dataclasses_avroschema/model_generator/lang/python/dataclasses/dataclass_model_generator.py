from dataclasses import dataclass

from dataclasses_avroschema.model_generator.lang.python import templates
from dataclasses_avroschema.model_generator.lang.python.base import BaseGenerator


@dataclass
class DataclassModelGenerator(BaseGenerator):
    def __post_init__(self) -> None:
        super().__post_init__()

        self.base_class = "AvroModel"
        # represent the decorator to add in the base class
        self.base_class_decorator = "@dataclasses.dataclass"

        self.imports.add("import dataclasses")
        self.imports.add("from dataclasses_avroschema import AvroModel")
        self.imports_dict = {
            "condecimal": "from dataclasses_avroschema.types import condecimal",
        }

        # Templates
        self.field_template = templates.field_template
