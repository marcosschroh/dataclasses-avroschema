import datetime
import io
import typing
import uuid

import fastavro

DATETIME_STR_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATE_STR_FORMAT = "%Y-%m-%d"
TIME_STR_FORMAT = "%H:%M:%S"


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


def deserialize(data: bytes, schema: typing.Dict, serialization_type: str = "avro") -> typing.Dict:
    if serialization_type == "avro":
        input_stream: typing.Union[io.BytesIO, io.StringIO] = io.BytesIO(data)

        payload = fastavro.schemaless_reader(input_stream, schema)

    elif serialization_type == "avro-json":
        input_stream = io.StringIO(data.decode())
        # This is an iterator, but not a container
        records = fastavro.json_reader(input_stream, schema)
        # records can have multiple payloads, but in this case we return the first one
        payload = list(records)[0]
    else:
        raise ValueError(f"Serialization type should be `avro` or `avro-json`, not {serialization_type}")

    input_stream.flush()

    return payload


def datetime_to_str(value: datetime.datetime) -> str:
    return value.strftime(DATETIME_STR_FORMAT)


def date_to_str(value: datetime.date) -> str:
    return value.strftime(DATE_STR_FORMAT)


def time_to_str(value: datetime.time) -> str:
    return value.strftime(TIME_STR_FORMAT)


def to_json(data: typing.Dict[str, typing.Any]) -> typing.Dict:
    json_data = {}

    for field, value in data.items():
        if isinstance(value, bytes):
            value = value.decode()
        elif isinstance(value, datetime.datetime):
            value = datetime_to_str(value)
        elif isinstance(value, datetime.date):
            value = date_to_str(value)
        elif isinstance(value, datetime.time):
            value = time_to_str(value)
        elif isinstance(value, uuid.UUID):
            value = str(value)

        json_data[field] = value

    return json_data
