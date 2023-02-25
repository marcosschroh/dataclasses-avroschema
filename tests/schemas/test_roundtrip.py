import json
from pathlib import Path

import pytest

from dataclasses_avroschema import BaseClassEnum, ModelGenerator

here = Path(__file__).parent.absolute()

marks = {
    "union_type": [
        pytest.mark.xfail(raises=RuntimeError, reason="model generator borks on difficult union namespaces")
    ],
    "decimal": [
        pytest.mark.xfail(raises=ValueError, reason="model generator looses decimal precision for default-null fields")
    ],
    "user_extra_avro_attributes": [
        pytest.mark.xfail(raises=AssertionError, reason="model generator does not handle aliases yet")
    ],
    "user_with_field_metadata": [
        pytest.mark.xfail(raises=AssertionError, reason="model generator does not support metadata yet")
    ],
    "union_default_type": [
        pytest.mark.xfail(raises=AssertionError, reason="schema generator does not handle enum comments yet")
    ],
    "user_self_reference_one_to_many": [
        pytest.mark.xfail(raises=AssertionError, reason="schema generator does not handle self references correctly")
    ],
    "user_self_reference_one_to_many_map": [
        pytest.mark.xfail(raises=ValueError, reason="schema generator does not handle self references correctly")
    ],
    "user_self_reference_one_to_one": [
        pytest.mark.xfail(raises=ValueError, reason="schema generator does not handle self references correctly")
    ],
}

avsc_files = [pytest.param(f, id=f.stem, marks=marks.get(f.stem, ())) for f in here.glob("avro/*.avsc")]


@pytest.mark.parametrize("schema", list(BaseClassEnum))
@pytest.mark.parametrize("filename", avsc_files)
def test_roundtrip(filename: Path, schema: BaseClassEnum):
    model_generator = ModelGenerator()
    schema = json.loads(filename.read_text())
    result = model_generator.render(schema=schema)

    try:
        code = compile(result, filename.with_suffix(".py").name, "exec")
    except Exception as e:
        raise RuntimeError(f"Failed to compile {filename}:\n" + result) from e

    ns = {}
    try:
        eval(code, ns)
    except Exception as e:
        raise RuntimeError(f"Failed to evaluate {filename}:\n" + result) from e
    assert True

    obj = ns[schema["name"]]
    new_schema = obj.avro_schema_to_python()
    assert new_schema == schema
