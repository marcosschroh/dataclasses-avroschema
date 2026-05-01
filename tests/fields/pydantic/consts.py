import pydantic

from dataclasses_avroschema.fields import field_utils

PYDANTIC_LOGICAL_TYPES = (
    # pydantic fields
    (
        pydantic.UUID1,
        {
            "type": field_utils.STRING,
            "logicalType": field_utils.UUID,
            "pydantic-class": "UUID1",
        },
    ),
    (
        pydantic.UUID3,
        {
            "type": field_utils.STRING,
            "logicalType": field_utils.UUID,
            "pydantic-class": "UUID3",
        },
    ),
    (
        pydantic.UUID4,
        {
            "type": field_utils.STRING,
            "logicalType": field_utils.UUID,
            "pydantic-class": "UUID4",
        },
    ),
    (
        pydantic.UUID5,
        {
            "type": field_utils.STRING,
            "logicalType": field_utils.UUID,
            "pydantic-class": "UUID5",
        },
    ),
)
