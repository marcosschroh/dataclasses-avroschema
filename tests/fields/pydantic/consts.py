import pydantic
from pydantic import v1

from dataclasses_avroschema.fields import field_utils

PYDANTIC_LOGICAL_TYPES_AND_DEFAULTS = (
    # pydantic fields
    (pydantic.UUID1, {"type": field_utils.STRING, "logicalType": field_utils.UUID, "pydantic-class": "UUID1"}),
    (pydantic.UUID3, {"type": field_utils.STRING, "logicalType": field_utils.UUID, "pydantic-class": "UUID3"}),
    (pydantic.UUID4, {"type": field_utils.STRING, "logicalType": field_utils.UUID, "pydantic-class": "UUID4"}),
    (pydantic.UUID5, {"type": field_utils.STRING, "logicalType": field_utils.UUID, "pydantic-class": "UUID5"}),
)

PYDANTIC_V1_LOGICAL_TYPES_AND_DEFAULTS = (
    # pydantic fields
    (v1.UUID1, {"type": field_utils.STRING, "logicalType": field_utils.UUID, "pydantic-class": "UUID1"}),
    (v1.UUID3, {"type": field_utils.STRING, "logicalType": field_utils.UUID, "pydantic-class": "UUID3"}),
    (v1.UUID4, {"type": field_utils.STRING, "logicalType": field_utils.UUID, "pydantic-class": "UUID4"}),
    (v1.UUID5, {"type": field_utils.STRING, "logicalType": field_utils.UUID, "pydantic-class": "UUID5"}),
)
