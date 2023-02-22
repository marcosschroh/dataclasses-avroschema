import json
import typing
from dataclasses import dataclass

import pytest

from dataclasses_avroschema import AvroModel
from tests.serialization.test_serialization import CLASSES_DATA_BINARY


@pytest.mark.parametrize("klass, data, avro_binary, avro_json, instance_json, python_dict", CLASSES_DATA_BINARY)
def test_to_dict_to_json(klass, data, avro_binary, avro_json, instance_json, python_dict):
    instance = klass(**data)

    assert instance.to_dict() == python_dict
    assert instance.to_json() == json.dumps(instance_json)


def test_dacite_config():
    @dataclass
    class Car(AvroModel):
        total: int

    @dataclass
    class Bus(AvroModel):
        driver: str
        total: int

    @dataclass
    class Trip(AvroModel):
        transport: typing.Union[Car, Bus]

    data = {"driver": "Marcos", "total": 10}
    bus = Bus.parse_obj(data=data)

    serialized_val = Trip(transport=bus).serialize()

    assert Trip.deserialize(serialized_val, create_instance=False) == {"transport": {"driver": "Marcos", "total": 10}}
    instance = Trip.deserialize(serialized_val)
    assert instance.transport == Car(total=10)


def test_custom_dacite_config():
    @dataclass
    class Car(AvroModel):
        total: int

    @dataclass
    class Bus(AvroModel):
        driver: str
        total: int

    @dataclass
    class Trip(AvroModel):
        transport: typing.Union[Car, Bus]

        class Meta:
            dacite_config = {
                "strict_unions_match": True,
                "strict": True,
            }

    data = {"driver": "Marcos", "total": 10}
    bus = Bus.parse_obj(data=data)

    serialized_val = Trip(transport=bus).serialize()
    assert Trip.deserialize(serialized_val, create_instance=False) == {"transport": {"driver": "Marcos", "total": 10}}
    instance = Trip.deserialize(serialized_val)
    assert instance.transport == bus
