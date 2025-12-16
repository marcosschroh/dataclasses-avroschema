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

from typing import Any, Dict

import pytest

from dataclasses_avroschema import ModelGenerator

model_generator = ModelGenerator()


def bench_render_model(schema: Dict[str, Any]) -> str:
    return model_generator.render(schema=schema)


@pytest.mark.benchmark(group="model_rendering")
@pytest.mark.parametrize(
    "fixture_name",
    (
        "schema",
        "schema_2",
        "schema_with_invalid_python_identifiers",
        "schema_with_python_keywords",
        "schema_with_no_fields",
        "schema_primitive_types_as_defined_types",
        "schema_with_nulls",
        "schema_with_unions",
        "schema_with_array_types",
        "schema_with_map_types",
        "schema_with_fixed_types",
        "schema_with_enum_types",
        "schema_with_enum_types_with_inner_default",
        "schema_enum_in_isolation",
        "schema_with_enum_types_case_sensitivity",
        "schema_with_enum_types_no_pascal_case",
        "schema_with_custom_inner_names",
        "schema_one_to_one_relationship",
        "schema_one_to_many_relationship_array_clashes_types",
        "schema_one_to_many_relationship_map_clashes_types",
        "schema_with_enum_clashes_types",
        "schema_one_to_many_relationship_multiple_clashes_types",
        "schema_one_to_many_relationship_with_late_clashes_types",
        "schema_one_to_many_relationship_union_with_clashes_types",
        "schema_one_to_many_array_relationship",
        "schema_one_to_one_relationship_clashes_types",
        "schema_one_to_many_map_relationship",
        "schema_one_to_self_relationship",
        "schema_with_multiple_levels_of_relationship",
        "schema_with_decimal_field",
        "schema_with_logical_types",
        "schema_with_logical_types_field_order",
        "schema_with_unknown_logical_types",
        "schema_with_pydantic_fields",
        "schema_with_pydantic_constrained_fields",
        "schema_with_pydantic_logical_fields",
        "with_fields_with_metadata",
        "logical_types_not_nested",
    ),
)
def test_render_model(benchmark, fixture_name: str, request: pytest.FixtureRequest):
    schema: Dict[str, Any] = request.getfixturevalue(fixture_name)
    benchmark(
        bench_render_model,
        schema,
    )
