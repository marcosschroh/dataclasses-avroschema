from dataclasses_avroschema import AvroField


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
