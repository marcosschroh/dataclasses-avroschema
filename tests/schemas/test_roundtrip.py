import json
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo

import pytest

from dataclasses_avroschema import AvroModel, BaseClassEnum, ModelGenerator

here = Path(__file__).parent.absolute()

marks = {
    "user_self_reference_one_to_many": [
        pytest.mark.xfail(
            raises=AssertionError,
            reason="schema generator does not handle self references correctly",
        )
    ],
    "user_self_reference_one_to_one": [
        pytest.mark.xfail(
            raises=ValueError,
            reason="schema generator does not handle self references correctly",
        )
    ],
}

avsc_files = [pytest.param(f, id=f.stem, marks=marks.get(f.stem, ())) for f in here.glob("avro/*.avsc")]
timezones = [ZoneInfo("CST6CDT"), ZoneInfo("Europe/London")]


@pytest.mark.parametrize("filename", avsc_files)
@pytest.mark.parametrize("timezone", timezones)
def test_roundtrip(filename: Path, timezone: str):
    base_class = BaseClassEnum.AVRO_MODEL.value

    if "pydantic_fields.avsc" in str(filename) or "logical_types_pydantic" in str(filename):
        base_class = BaseClassEnum.AVRO_DANTIC_MODEL.value

    model_generator = ModelGenerator(base_class=base_class)
    schema = json.loads(filename.read_text())
    result = model_generator.render(schema=schema)
    print(result)

    try:
        code = compile(result, filename.with_suffix(".py").name, "exec")
    except Exception as e:
        raise RuntimeError(f"Failed to compile {filename}:\n" + result) from e

    ns: Dict[str, AvroModel] = {}
    try:
        eval(code, ns)
        print(code)
    except Exception as e:
        raise RuntimeError(f"Failed to evaluate {filename}:\n" + result) from e
    assert True

    obj = ns[schema["name"]]
    new_schema = obj.avro_schema_to_python()

    assert new_schema == schema
