import dataclasses
import enum
import json
import typing
from concurrent.futures import ThreadPoolExecutor

from fastavro import parse_schema

from dataclasses_avroschema import AvroModel


@dataclasses.dataclass
class ConcurrentChild(AvroModel):
    value: str


@dataclasses.dataclass
class ConcurrentParent(AvroModel):
    child: ConcurrentChild
    tags: typing.List[ConcurrentChild] = dataclasses.field(default_factory=list)


def _assert_valid_schema(schema: str) -> None:
    # `parse_schema` raises (e.g. `UnknownType`) when a named type is referenced
    # without being defined inline, which is exactly what the race used to emit.
    parse_schema(json.loads(schema))


def test_concurrent_schema_generation_is_thread_safe():
    """
    Concurrent calls to ``avro_schema`` for a model with nested records must
    always produce valid, self-contained schemas.
    """
    errors: typing.List[BaseException] = []

    def worker() -> None:
        for _ in range(50):
            try:
                _assert_valid_schema(ConcurrentParent.avro_schema())
            except BaseException as exc:  # pragma: no cover - only populated on regression
                errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker) for _ in range(8)]
        for future in futures:
            future.result()

    assert not errors


def test_concurrent_schema_generation_with_enum():
    """
    The race also affects enum fields, which share the same ``_user_defined_types``
    bookkeeping. Concurrent generation for a record with both nested records and
    enums must stay valid.
    """

    class Status(enum.Enum):
        PENDING = "PENDING"
        DONE = "DONE"

    @dataclasses.dataclass
    class EnumParent(AvroModel):
        status: Status
        child: ConcurrentChild

    errors: typing.List[BaseException] = []

    def worker() -> None:
        for _ in range(50):
            try:
                _assert_valid_schema(EnumParent.avro_schema())
            except BaseException as exc:  # pragma: no cover - only populated on regression
                errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker) for _ in range(8)]
        for future in futures:
            future.result()

    assert not errors


def test_concurrent_schema_generation_independent_models():
    """
    Independent model graphs generated concurrently must each render correctly.
    This also guards against a lock implementation that serializes on a single
    global lock and accidentally corrupts state across unrelated models.
    """

    @dataclasses.dataclass
    class Left(AvroModel):
        value: int

    @dataclasses.dataclass
    class Right(AvroModel):
        value: str

    errors: typing.List[BaseException] = []

    def worker_left() -> None:
        for _ in range(50):
            try:
                _assert_valid_schema(Left.avro_schema())
            except BaseException as exc:  # pragma: no cover
                errors.append(exc)

    def worker_right() -> None:
        for _ in range(50):
            try:
                _assert_valid_schema(Right.avro_schema())
            except BaseException as exc:  # pragma: no cover
                errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker_left) for _ in range(4)] + [executor.submit(worker_right) for _ in range(4)]
        for future in futures:
            future.result()

    assert not errors
