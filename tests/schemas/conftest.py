import json
import os

import pytest

AVRO_SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avro")


def load(fp):
    with open(fp, mode="r") as f:
        return f.read()


def load_json(file_name):
    schema_path = os.path.join(AVRO_SCHEMAS_DIR, file_name)
    schema_string = load(schema_path)
    return json.loads(schema_string)


@pytest.fixture
def user_avro_json():
    return load_json("user.avsc")


@pytest.fixture
def user_with_field_metadata_avro_json():
    return load_json("user_with_field_metadata.avsc")


@pytest.fixture
def user_v2_avro_json():
    return load_json("user_v2.avsc")


@pytest.fixture
def user_advance_avro_json():
    return load_json("user_advance.avsc")


@pytest.fixture
def user_advance_with_defaults_avro_json():
    return load_json("user_advance_with_defaults.avsc")


@pytest.fixture
def user_extra_avro_attributes():
    return load_json("user_extra_avro_attributes.avsc")


@pytest.fixture
def user_one_address_schema():
    return load_json("user_one_address.avsc")


@pytest.fixture
def user_one_address_alias_item():
    return load_json("user_one_address_alias_item.avsc")


@pytest.fixture
def user_one_address_schema_with_none_default():
    return load_json("user_one_address_with_none_default.avsc")


@pytest.fixture
def user_many_address_schema():
    return load_json("user_many_address.avsc")


@pytest.fixture
def user_many_address_map_schema():
    return load_json("user_many_address_map.avsc")


@pytest.fixture
def user_many_address_map_schema_alias_item():
    return load_json("user_many_address_map_alias_item.avsc")


@pytest.fixture
def user_self_reference_one_to_one_schema():
    return load_json("user_self_reference_one_to_one.avsc")


@pytest.fixture
def user_self_reference_one_to_many_schema():
    return load_json("user_self_reference_one_to_many.avsc")


@pytest.fixture
def user_self_reference_one_to_many_map_schema():
    return load_json("user_self_reference_one_to_many_map.avsc")


@pytest.fixture
def logical_types_schema():
    return load_json("logical_types.avsc")


@pytest.fixture
def union_type_schema():
    return load_json("union_type.avsc")


@pytest.fixture
def default_union_schema():
    return load_json("union_default_type.avsc")


@pytest.fixture
def typing_optional_schema():
    return load_json("union_typing_optional.avsc")


@pytest.fixture
def decimal_types_schema():
    return load_json("decimal.avsc")
