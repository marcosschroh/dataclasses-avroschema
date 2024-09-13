import enum
import logging
import typing
from dataclasses import dataclass, field

import fastavro

from dataclasses_avroschema.types import JsonDict

from .lang.python.avrodantic.avrodantic_model_generator import AvroDanticModelGenerator
from .lang.python.base import BaseGenerator
from .lang.python.dataclasses.dataclass_model_generator import DataclassModelGenerator
from .lang.python.pydantic.pydantic_model_generator import PydanticModelGenerator

logger = logging.getLogger(__name__)


class BaseClassEnum(str, enum.Enum):
    AVRO_MODEL = "AvroModel"
    PYDANTIC_MODEL = "BaseModel"
    AVRO_DANTIC_MODEL = "AvroBaseModel"


class ModelType(str, enum.Enum):
    AVRODANTIC = "avrodantic"
    DATACLASS = "dataclass"
    PYDANTIC = "pydantic"


@dataclass
class ModelGenerator:
    """
    ModelGenerator converts an avro schema to classes

    **`Avro schema` --> `Python class`**

    This class will be in charge of render all the python types in a proper way.
    The rendered result is a string that contains proper identation, decorators, imports
    and any extras so the result can be saved in a file and it will be ready to use.

    !!! Example
        ```python
        from dataclasses_avroschema import ModelGenerator

        model_generator = ModelGenerator()

        schema = {
            "type": "record",
            "namespace": "com.kubertenes",
            "name": "AvroDeployment",
            "fields": [
                {"name": "image", "type": "string"},
                {"name": "replicas", "type": "int"},
                {"name": "port", "type": "int"},
            ],
        }

        result = model_generator.render(schema=schema)

        # save the result in a file
        with open("models.py", mode="+w") as f:
            f.write(result)
        ```

    Then explore the module `models.py`, the result must be

    ```python title="Code generated"
    import dataclasses

    from dataclasses_avroschema import AvroModel
    from dataclasses_avroschema import types


    @dataclasses.dataclass
    class AvroDeployment(AvroModel):
        image: str
        replicas: types.Int32
        port: types.Int32

        class Meta:
            namespace = "com.kubertenes"
    ```
    """

    base_class: str = BaseClassEnum.AVRO_MODEL.value
    include_original_schema: bool = False
    model_type_mapper: typing.Dict[str, BaseGenerator] = field(init=False)

    def __post_init__(self) -> None:
        # This mapper should be oppulated on run time and be available using pluigns
        self.model_type_mapper = {
            ModelType.AVRODANTIC: AvroDanticModelGenerator(include_original_schema=self.include_original_schema),
            ModelType.DATACLASS: DataclassModelGenerator(include_original_schema=self.include_original_schema),
            ModelType.PYDANTIC: PydanticModelGenerator(include_original_schema=self.include_original_schema),
            # The following code should be removed
            BaseClassEnum.AVRO_DANTIC_MODEL: AvroDanticModelGenerator(
                include_original_schema=self.include_original_schema
            ),
            BaseClassEnum.AVRO_MODEL: DataclassModelGenerator(include_original_schema=self.include_original_schema),
            BaseClassEnum.PYDANTIC_MODEL: PydanticModelGenerator(include_original_schema=self.include_original_schema),
        }

    @staticmethod
    def validate_schema(*, schemas: typing.List[JsonDict]) -> None:
        """
        Validate that the schemas are valid avro schemas
        """
        fastavro.parse_schema(schemas)

    def render(
        self,
        *,
        schema: JsonDict,
        model_type: typing.Optional[str] = None,
        include_original_schema: bool = False,
    ) -> str:
        """
        Render the module with the classes generated from the schema
        """
        return self.render_module(
            schemas=[schema], model_type=model_type, include_original_schema=include_original_schema
        )

    def render_module(
        self,
        *,
        schemas: typing.List[JsonDict],
        model_type: typing.Optional[str] = None,
        include_original_schema: bool = False,
    ) -> str:
        """
        Render the module with the classes generated from the schemas
        """

        self.validate_schema(schemas=schemas)

        if model_type is None:
            logger.warning(
                "Call `render` with the `generator` option instead so you can reuse the ModelGenerator "
                "for rendering different models. "
                "Example: https://marcosschroh.github.io/dataclasses-avroschema/model_generator/#usage"
            )

        generator_name = model_type or self.base_class
        model_generator = self.model_type_mapper[generator_name]

        # This needs to be properly implemented and has to be a parameter in the `render`
        model_generator.include_original_schema = include_original_schema

        return model_generator.render(schemas=schemas)
