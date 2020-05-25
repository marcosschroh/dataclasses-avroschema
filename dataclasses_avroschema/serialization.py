import io
import typing

import fastavro


def serialize(payload: typing.Dict, schema: typing.Dict, serialization_type: str = "avro") -> bytes:
    if serialization_type == "avro":
        file_like_output = io.BytesIO()

        fastavro.schemaless_writer(file_like_output, schema, payload)

        value = file_like_output.getvalue()
    elif serialization_type == "avro-json":
        file_like_output = io.StringIO()
        fastavro.json_writer(file_like_output, schema, [payload])
        value = file_like_output.getvalue().encode("utf-8")
    else:
        raise ValueError(f"Serialization type should be `avro` or `avro-json`, not {serialization_type}")

    file_like_output.flush()

    return value


def deserialize(data: bytes, schema: typing.Dict, serialization_type: str = "avro") -> typing.Any:
    if serialization_type == "avro":
        input_stream = io.BytesIO(data)

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
