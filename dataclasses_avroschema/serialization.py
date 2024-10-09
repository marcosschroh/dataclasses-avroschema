import datetime
import decimal
import enum
import io
import typing
import uuid

import fastavro

from .types import JsonDict

if typing.TYPE_CHECKING:
    from .main import CT  # pragma: no cover

DATETIME_STR_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATE_STR_FORMAT = "%Y-%m-%d"
TIME_STR_FORMAT = "%H:%M:%S"

decimal_context = decimal.Context()


def serialize(payload: typing.Dict, schema: typing.Dict, serialization_type: str = "avro") -> bytes:
    if serialization_type == "avro":
        file_like_output: typing.Union[io.BytesIO, io.StringIO] = io.BytesIO()

        fastavro.schemaless_writer(file_like_output, schema, payload)

        value = file_like_output.getvalue()
    elif serialization_type == "avro-json":
        file_like_output = io.StringIO()
        fastavro.json_writer(file_like_output, schema, [payload])
        value = file_like_output.getvalue().encode("utf-8")
    else:
        raise ValueError(f"Serialization type should be `avro` or `avro-json`, not {serialization_type}")

    file_like_output.flush()

    return value  # type: ignore


def deserialize(
    *,
    data: bytes,
    schema: JsonDict,
    model: "CT",
    serialization_type: str = "avro",
    writer_schema: typing.Optional[JsonDict] = None,
) -> JsonDict:
    if serialization_type == "avro":
        input_stream: typing.Union[io.BytesIO, io.StringIO] = io.BytesIO(data)

        payload = fastavro.schemaless_reader(
            input_stream,
            writer_schema=writer_schema or schema,
            reader_schema=schema,
            return_record_name=True,
            return_record_name_override=True,
        )

    elif serialization_type == "avro-json":
        input_stream = io.StringIO(data.decode())
        # This is an iterator, but not a container
        records = fastavro.json_reader(input_stream, schema)
        # records can have multiple payloads, but in this case we return the first one
        payload = list(records)[0]
    else:
        raise ValueError(f"Serialization type should be `avro` or `avro-json`, not {serialization_type}")

    input_stream.flush()

    return sanitize_payload(data=payload, model=model)  # type: ignore


def sanitize_payload(*, data: JsonDict, model: "CT") -> JsonDict:
    """
    This function tries to convert cast all the cases that have
    `unions` with a Tuple format (AvroType, payload), for example
    (Car, {"brand": "fiat"}). This cases happens when there are
    avro unions of records which are similar or equals among them
    """
    cleaned_data = {}
    for field_name, field_value in data.items():
        if isinstance(field_value, dict):
            field_value = sanitize_payload(data=field_value, model=model)
        elif isinstance(field_value, tuple) and len(field_value) == 2:
            field_value = sanitize_union(union=field_value, model=model)

        cleaned_data[field_name] = field_value

    return cleaned_data


def sanitize_union(*, union: typing.Tuple, model: "CT") -> typing.Optional["CT"]:
    # the first value is the model/record name and the second is its payload
    model_name, model_value = union
    if isinstance(model_value, dict):
        # it can be a dict again so we need to sanitize
        model_value = sanitize_payload(data=model_value, model=model)

    model_name = model_name.split(".")[-1]

    avro_model = model.get_user_defined_type(name=model_name)
    if avro_model is not None:
        return avro_model.parse_obj(model_value)

    return model_value


def datetime_to_str(value: datetime.datetime) -> str:
    return value.strftime(DATETIME_STR_FORMAT)


def date_to_str(value: datetime.date) -> str:
    return value.strftime(DATE_STR_FORMAT)


def time_to_str(value: datetime.time) -> str:
    return value.strftime(TIME_STR_FORMAT)


def decimal_to_str(value: decimal.Decimal, precision: int, scale: int = 0) -> str:
    value_bytes = prepare_bytes_decimal(value, precision, scale)
    return r"\u" + value_bytes.hex()


def string_to_decimal(*, value: str, schema: JsonDict) -> decimal.Decimal:
    # first remove the Unicode character
    value = value.replace(r"\u", "")

    # then concert to bytes
    decimal_bytes = bytes.fromhex(value)

    # finally get the decimal.Decimal
    scale = schema.get("scale", 0)
    precision = schema["precision"]
    unscaled_datum = int.from_bytes(decimal_bytes, byteorder="big", signed=True)
    decimal_context.prec = precision

    return decimal_context.create_decimal(unscaled_datum).scaleb(-scale, decimal_context)


# This is an almost complete copy of fastavro's _logical_writers_py.prepare_bytes_decimal
# the only tweak is to pass in scale/precision directly instead of a schema
# This is needed to properly serialize a default decimal.Decimal into the avro schema
def prepare_bytes_decimal(data: decimal.Decimal, precision: int, scale: int = 0) -> bytes:
    """Convert decimal.Decimal to bytes"""
    sign, digits, exp = data.as_tuple()

    if len(digits) > precision:
        raise ValueError("The decimal precision is bigger than allowed by schema")

    delta = int(exp) + scale

    if delta < 0:
        raise ValueError("Scale provided in schema does not match the decimal")

    unscaled_datum = 0
    for digit in digits:
        unscaled_datum = (unscaled_datum * 10) + digit

    unscaled_datum = 10**delta * unscaled_datum

    bytes_req = (unscaled_datum.bit_length() + 8) // 8

    if sign:
        unscaled_datum = -unscaled_datum

    return unscaled_datum.to_bytes(bytes_req, byteorder="big", signed=True)


def serialize_value(*, value: typing.Any) -> typing.Any:
    from .main import AvroModel

    if isinstance(value, bytes):
        value = value.decode()
    elif isinstance(value, datetime.datetime):
        value = datetime_to_str(value)
    elif isinstance(value, datetime.date):
        value = date_to_str(value)
    elif isinstance(value, datetime.time):
        value = time_to_str(value)
    elif isinstance(value, (uuid.UUID, decimal.Decimal)):
        value = str(value)
    elif isinstance(value, dict):
        value = to_json(value)
    elif isinstance(value, enum.Enum):
        value = value.value
    elif isinstance(value, (list, tuple)):
        value = type(value)(serialize_value(value=item) for item in value)
    elif isinstance(value, AvroModel):
        value = to_json(value.asdict())

    return value


def to_json(data: JsonDict) -> JsonDict:
    json_data = {}

    for field, value in data.items():
        json_data[field] = serialize_value(value=value)

    return json_data
