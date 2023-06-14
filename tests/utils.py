import dataclasses

from dataclasses_avroschema import AvroModel, types
from dataclasses_avroschema.avrodantic import AvroBaseModel


# dataclass decorator for parametrized creation of models from AvroModel and
# AvroBaseModel

def conditional_dataclass(klass: type):
        if issubclass(klass, AvroBaseModel):
            return klass
        return dataclasses.dataclass(klass)
