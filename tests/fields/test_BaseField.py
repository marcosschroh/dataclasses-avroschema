from dataclasses_avroschema import fields


def test_render():
    field = fields.Field("first_name", str, fields.NULL, metadata={"desc": "English Language Name"})

    expected = {
        "name": "first_name",
        "type": ["string", fields.NULL],
        "default": fields.NULL,
        "desc": "English Language Name",
    }

    assert expected == field.render()

    field = fields.Field("engine_name", str, fields.NULL)

    expected = {
        "name": "engine_name",
        "type": ["string", fields.NULL],
        "default": fields.NULL,
    }

    assert expected == field.render()

    field = fields.Field(
        "breed_name", str, fields.NULL, metadata={"encoding": "some_exotic_encoding", "doc": "Official Breed Name"},
    )

    expected = {
        "name": "breed_name",
        "type": ["string", fields.NULL],
        "default": fields.NULL,
        "encoding": "some_exotic_encoding",
        "doc": "Official Breed Name",
    }

    assert expected == field.render()


def test_render_metadata():
    field = fields.Field("first_name", str, fields.NULL, metadata={"desc": "English Language Name"})

    expected = [("desc", "English Language Name")]

    assert expected == field.get_metadata()

    field = fields.Field("engine_name", str, fields.NULL)

    expected = []

    assert expected == field.get_metadata()

    field = fields.Field(
        "breed_name", str, fields.NULL, metadata={"encoding": "some_exotic_encoding", "doc": "Official Breed Name"},
    )

    expected = [("encoding", "some_exotic_encoding"), ("doc", "Official Breed Name")]

    assert expected == field.get_metadata()
