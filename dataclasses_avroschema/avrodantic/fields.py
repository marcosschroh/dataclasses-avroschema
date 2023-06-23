from dataclasses_avroschema.faker import fake
from dataclasses_avroschema.fields import fields


class FilePathField(fields.StringField):
    def fake(self) -> str:
        return fake.pystr()
