import dataclasses
import inspect
import typing
from collections import OrderedDict


@dataclasses.dataclass
class BaseSchemaDefinition:
    """
    Minimal Schema definition
    """
    type: str
    fields: list
    klass_or_instance: dataclasses.dataclass

    def get_rendered_fields(self):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError

    def get_schema_name(self):
        if inspect.isclass(self.klass_or_instance):
            return self.klass_or_instance.__name__
        return self.klass_or_instance.__class__.__name__

    def generate_documentation(self):
        doc = self.klass_or_instance.__doc__

        if doc is not None:
            return doc.replace("\n", "")


@dataclasses.dataclass
class AvroSchemaDefinition(BaseSchemaDefinition):

    include_schema_doc: bool = True

    def get_rendered_fields(self):
        return [
            field.render() for field in self.fields
        ]

    # def get_aliases(self):
    #     if self.typing.ClassVar

    def render(self):
        schema = OrderedDict([
            ("type", self.type),
            ("name", self.get_schema_name()),
            ("fields", self.get_rendered_fields())
        ])

        # if self.aliases:
        #     schema["aliases"] = self.aliases

        if self.include_schema_doc:
            doc = self.generate_documentation()
            if doc is not None:
                schema["doc"] = doc

        return schema
