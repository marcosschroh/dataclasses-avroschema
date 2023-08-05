import dataclasses
from datetime import datetime

from dataclasses_avroschema import AvroField, AvroModel, utils


def test_render():
    field = AvroField("first_name", str, metadata={"desc": "English Language Name"})

    expected = {
        "name": "first_name",
        "type": "string",
        "desc": "English Language Name",
    }

    assert expected == field.render()

    field = AvroField("engine_name", str)

    expected = {
        "name": "engine_name",
        "type": "string",
    }

    assert expected == field.render()

    field = AvroField(
        "breed_name",
        str,
        default="test",
        metadata={"encoding": "some_exotic_encoding", "doc": "Official Breed Name"},
    )

    expected = {
        "name": "breed_name",
        "type": "string",
        "default": "test",
        "encoding": "some_exotic_encoding",
        "doc": "Official Breed Name",
    }

    assert expected == field.render()


def test_render_metadata():
    field = AvroField("first_name", str, metadata={"desc": "English Language Name"})

    expected = [("desc", "English Language Name")]

    assert expected == field.get_metadata()

    field = AvroField("engine_name", str)

    expected = []

    assert expected == field.get_metadata()

    field = AvroField(
        "breed_name",
        str,
        metadata={"encoding": "some_exotic_encoding", "doc": "Official Breed Name"},
    )

    expected = [("encoding", "some_exotic_encoding"), ("doc", "Official Breed Name")]

    assert expected == field.get_metadata()


def test_render_complex_types():
    @dataclasses.dataclass
    class Metadata(AvroModel):
        timestamp: datetime = dataclasses.field(
            default_factory=lambda: datetime(2023, 10, 21, 11, 11),
        )

    parent = AvroModel()
    parent.metadata = utils.SchemaMetadata.create(type)
    field = AvroField(
        "metadata",
        Metadata,
        metadata={"desc": "Some metadata"},
        default_factory=Metadata,
        parent=parent,
    )

    expected = {
        "desc": "Some metadata",
        "name": "metadata",
        "type": {
            "type": "record",
            "name": "Metadata",
            "fields": [
                {
                    "name": "timestamp",
                    "type": {"type": "long", "logicalType": "timestamp-millis"},
                    "default": 1697886660000,
                }
            ],
        },
        "default": {"timestamp": "2023-10-21T11:11:00"},
    }

    assert expected == dict(field.render())
