from dataclasses import dataclass

from dataclasses_avroschema.model_generator.lang.python import templates
from dataclasses_avroschema.model_generator.lang.python.base import BaseGenerator
from dataclasses_avroschema.types import JsonDict


@dataclass
class DataclassModelGenerator(BaseGenerator):
    def __post_init__(self) -> None:
        super().__post_init__()

        self.base_class = "AvroModel"
        # represent the decorator to add in the base class
        self.base_class_decorator = "@dataclasses.dataclass"
        self.imports_dict = {
            "condecimal": "from dataclasses_avroschema.types import condecimal",
        }

        # Templates
        self.field_template = templates.field_template

    def add_class_imports(self) -> None:
        self.imports.add("import dataclasses")
        self.imports.add("from dataclasses_avroschema import AvroModel")

    def _resolve_type_from_metadata(self, *, field: JsonDict) -> None:
        return None
