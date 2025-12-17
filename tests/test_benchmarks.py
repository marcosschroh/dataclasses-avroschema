"""
This file contians benchmarks for kstreams.

Interpreting the data:

- Name: Name of the test or function being benchmarked.
- Min: The shortest execution time recorded across all runs.
- Max: The longest execution time recorded.
- Mean: The average execution time across all runs.
- StdDev: The standard deviation of execution times, representing the variability of the
    measurements. A low value indicates consistent performance.
- Median: The middle value when all execution times are sorted.
- IQR (Interquartile Range): The range between the 25th and 75th percentile of execution
    times. It’s a robust measure of variability that’s less sensitive to outliers.
- Outliers: Measurements that significantly differ from others.
    E.g., 5;43 means 5 mild and 43 extreme outliers.
- OPS (Operations Per Second): How many times the function could execute
    in one second (calculated as 1 / Mean).
- Rounds: The number of times the test was run.
- Iterations: Number of iterations per round.

Performance may be affected by:
- Power-saving modes
- CPU frequency scaling
- Background Processes

To get accurate results, run benchmarks on a dedicated machine with no other
applications running.

## Profiling

Profile and visualize your code with `py-spy`:

```python
pip install py-spy
sudo py-spy record -o profile.svg -- python tests/test_benchmarks.py
```
"""

import time
from typing import Any, Callable, Dict, Type

import pytest

from dataclasses_avroschema import AvroModel


def bench_render_avro_schema(model: Type[AvroModel]) -> str:
    return model.avro_schema()


def bench_render_avro_schema_to_python(model: Type[AvroModel]) -> Dict[str, Any]:
    return model.avro_schema_to_python()


def bench_fake(model: Type[AvroModel]) -> AvroModel:
    return model.fake()


def bench_avro_serialization(model: Type[AvroModel]) -> None:
    instance = model.fake()
    start = time.time()
    encoded = instance.serialize()
    model.deserialize(encoded)
    end = time.time()
    result = end - start
    limit = 0.2  # 200 milliseconds
    assert result < limit, f"{result} is not lower than {limit}"  # Serialization and deserialization should be fast


@pytest.mark.benchmark(group="avro_schema_rendering")
@pytest.mark.parametrize(
    "fixture_name",
    (
        "user_dataclass",
        "user_dataclass_with_doc",
        "user_dataclass_with_field_metadata",
        "user_v2_dataclass",
        "user_extra_avro_atributes_dataclass",
        "user_advance_dataclass",
        "user_advance_dataclass_with_enum",
        "user_advance_dataclass_with_union_enum",
        "user_advance_dataclass_with_union_enum_with_annotated",
        "user_advance_dataclass_with_sub_record_and_enum",
        "user_advance_with_defaults_dataclass",
        "user_advance_with_defaults_dataclass_with_enum",
    ),
)
def test_render_avro_schema(benchmark, fixture_name: str, request: pytest.FixtureRequest):
    model: Callable[[], AvroModel] = request.getfixturevalue(fixture_name)
    benchmark(
        bench_render_avro_schema,
        model,
    )


@pytest.mark.benchmark(group="avro_schema_to_python_rendering")
@pytest.mark.parametrize(
    "fixture_name",
    (
        "user_dataclass",
        "user_dataclass_with_doc",
        "user_dataclass_with_field_metadata",
        "user_v2_dataclass",
        "user_extra_avro_atributes_dataclass",
        "user_advance_dataclass",
        "user_advance_dataclass_with_enum",
        "user_advance_dataclass_with_union_enum",
        "user_advance_dataclass_with_union_enum_with_annotated",
        "user_advance_dataclass_with_sub_record_and_enum",
        "user_advance_with_defaults_dataclass",
        "user_advance_with_defaults_dataclass_with_enum",
    ),
)
def test_render_avro_schema_to_python(benchmark, fixture_name: str, request: pytest.FixtureRequest):
    model: Callable[[], AvroModel] = request.getfixturevalue(fixture_name)
    benchmark(
        bench_render_avro_schema_to_python,
        model,
    )


@pytest.mark.benchmark(group="fake_data_generation")
@pytest.mark.parametrize(
    "fixture_name",
    (
        "user_dataclass",
        "user_dataclass_with_doc",
        "user_dataclass_with_field_metadata",
        "user_v2_dataclass",
        "user_extra_avro_atributes_dataclass",
        "user_advance_dataclass",
        "user_advance_dataclass_with_enum",
        "user_advance_dataclass_with_union_enum",
        "user_advance_dataclass_with_union_enum_with_annotated",
        "user_advance_dataclass_with_sub_record_and_enum",
        "user_advance_with_defaults_dataclass",
        "user_advance_with_defaults_dataclass_with_enum",
    ),
)
def test_fake(benchmark, fixture_name: str, request: pytest.FixtureRequest):
    model: Callable[[], AvroModel] = request.getfixturevalue(fixture_name)
    benchmark(
        bench_fake,
        model,
    )


@pytest.mark.benchmark(group="binary_serialization")
@pytest.mark.parametrize(
    "fixture_name",
    (
        "user_dataclass",
        "user_dataclass_with_doc",
        "user_dataclass_with_field_metadata",
        "user_v2_dataclass",
        "user_extra_avro_atributes_dataclass",
        "user_advance_dataclass",
        "user_advance_dataclass_with_enum",
        "user_advance_dataclass_with_union_enum",
        "user_advance_dataclass_with_union_enum_with_annotated",
        "user_advance_dataclass_with_sub_record_and_enum",
        "user_advance_with_defaults_dataclass",
        "user_advance_with_defaults_dataclass_with_enum",
    ),
)
def test_serialization(benchmark, fixture_name: str, request: pytest.FixtureRequest):
    model: Callable[[], AvroModel] = request.getfixturevalue(fixture_name)
    benchmark(
        bench_avro_serialization,
        model,
    )
