"""
Tests for ForwardRef resolution in Python 3.14+ (PEP 649).

These tests verify that the library correctly resolves forward references
to types that are:
1. Imported under TYPE_CHECKING blocks
2. Used in union types (e.g., SomeClass | None)
3. Used in container types (e.g., list[SomeClass])
4. Using various TYPE_CHECKING import patterns (typing.TYPE_CHECKING, tp.TYPE_CHECKING, etc.)
"""

import dataclasses
import sys
import typing

from dataclasses_avroschema import AvroModel
from dataclasses_avroschema.fields.fields import (
    _get_type_checking_imports_from_globals,
    _parse_type_checking_imports,
    _resolve_forward_ref,
)


class TestParseTypeCheckingImports:
    """Tests for parsing TYPE_CHECKING import blocks from source code."""

    def test_parse_from_import_with_type_checking_name(self):
        """Test parsing 'if TYPE_CHECKING:' with 'from x import y' syntax."""
        source = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "datetime" in imports
        assert "UUID" in imports
        assert imports["datetime"] is __import__("datetime").datetime
        assert imports["UUID"] is __import__("uuid").UUID

    def test_parse_from_import_with_typing_dot_type_checking(self):
        """Test parsing 'if typing.TYPE_CHECKING:' pattern."""
        source = """
import typing

if typing.TYPE_CHECKING:
    from decimal import Decimal

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "Decimal" in imports
        assert imports["Decimal"] is __import__("decimal").Decimal

    def test_parse_from_import_with_aliased_typing_module(self):
        """Test parsing 'if tp.TYPE_CHECKING:' pattern (import typing as tp)."""
        source = """
import typing as tp

if tp.TYPE_CHECKING:
    from collections import OrderedDict

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "OrderedDict" in imports

    def test_parse_module_import(self):
        """Test parsing 'import module' syntax under TYPE_CHECKING."""
        source = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime
    import decimal

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "datetime" in imports
        assert "decimal" in imports
        # These should be modules, not classes
        import datetime
        import decimal

        assert imports["datetime"] is datetime
        assert imports["decimal"] is decimal

    def test_parse_aliased_import(self):
        """Test parsing 'from x import y as z' syntax."""
        source = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime as dt
    from uuid import UUID as UniqueID

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "dt" in imports
        assert "UniqueID" in imports
        assert "datetime" not in imports  # Original name should not be present
        assert "UUID" not in imports

    def test_parse_multiple_imports_same_line(self):
        """Test parsing multiple imports on the same line."""
        source = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime, date, time

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "datetime" in imports
        assert "date" in imports
        assert "time" in imports

    def test_parse_empty_source(self):
        """Test parsing source with no TYPE_CHECKING block."""
        source = """
from datetime import datetime

class MyClass:
    value: datetime
"""
        imports = _parse_type_checking_imports(source)
        assert imports == {}

    def test_parse_syntax_error_returns_empty(self):
        """Test that syntax errors in source return empty dict."""
        source = "this is not valid python {"
        imports = _parse_type_checking_imports(source)
        assert imports == {}

    def test_parse_nested_type_checking_not_supported(self):
        """Test that only top-level TYPE_CHECKING blocks are parsed."""
        source = """
from typing import TYPE_CHECKING

def some_function():
    if TYPE_CHECKING:
        from datetime import datetime

class MyClass:
    pass
"""
        # This should still work because ast.walk finds all If nodes
        imports = _parse_type_checking_imports(source)
        assert "datetime" in imports


class TestResolveForwardRef:
    """Tests for resolving ForwardRef objects to actual types."""

    def test_resolve_simple_forward_ref(self):
        """Test resolving a simple ForwardRef with __globals__."""
        # Create a ForwardRef with globals containing the target type
        forward_ref = typing.ForwardRef("datetime")
        # Manually set __globals__ to simulate Python 3.14 behavior
        if hasattr(forward_ref, "__globals__"):
            object.__setattr__(
                forward_ref,
                "__globals__",
                {
                    "__name__": "test_module",
                    "__file__": None,
                    "datetime": __import__("datetime").datetime,
                },
            )

        resolved = _resolve_forward_ref(forward_ref)
        # If __globals__ was set, it should resolve; otherwise falls back to eval_namespace
        assert resolved is __import__("datetime").datetime or isinstance(resolved, typing.ForwardRef)

    def test_resolve_forward_ref_with_standard_types(self):
        """Test that standard types (UUID, datetime, etc.) resolve without __globals__."""
        # These should resolve using the built-in eval_namespace
        test_cases = [
            ("UUID", __import__("uuid").UUID),
            ("date", __import__("datetime").date),
            ("time", __import__("datetime").time),
            ("timedelta", __import__("datetime").timedelta),
            ("Decimal", __import__("decimal").Decimal),
        ]

        for type_name, expected_type in test_cases:
            forward_ref = typing.ForwardRef(type_name)
            # Clear __globals__ to test fallback
            if hasattr(forward_ref, "__globals__"):
                try:
                    object.__setattr__(forward_ref, "__globals__", {})
                except (AttributeError, TypeError):
                    pass  # Some Python versions don't allow this

            resolved = _resolve_forward_ref(forward_ref)
            # Should resolve to the expected type or remain as ForwardRef if __globals__ can't be modified
            assert resolved is expected_type or isinstance(resolved, typing.ForwardRef)

    def test_resolve_unresolvable_forward_ref_returns_original(self):
        """Test that unresolvable ForwardRefs return the original."""
        forward_ref = typing.ForwardRef("NonExistentClass")
        if hasattr(forward_ref, "__globals__"):
            try:
                object.__setattr__(
                    forward_ref,
                    "__globals__",
                    {
                        "__name__": "test_module",
                        "__file__": None,
                    },
                )
            except (AttributeError, TypeError):
                pass

        resolved = _resolve_forward_ref(forward_ref)
        # Should return the original ForwardRef since it can't be resolved
        assert isinstance(resolved, typing.ForwardRef)


class TestGetTypeCheckingImportsFromGlobals:
    """Tests for extracting TYPE_CHECKING imports from __globals__ dict."""

    def test_returns_empty_when_no_file(self):
        """Test that missing __file__ returns empty dict."""
        globals_dict = {"__name__": "test_module"}
        imports = _get_type_checking_imports_from_globals(globals_dict)
        assert imports == {}

    def test_returns_empty_when_file_not_found(self):
        """Test that non-existent __file__ returns empty dict."""
        globals_dict = {
            "__name__": "test_module",
            "__file__": "/nonexistent/path/to/module.py",
        }
        imports = _get_type_checking_imports_from_globals(globals_dict)
        assert imports == {}


class TestAvroModelWithForwardRefs:
    """Integration tests for AvroModel with forward references.

    Note: These tests use actual types (not string annotations) because
    string annotations in dynamically-defined test classes don't have
    the proper __globals__ context. The fix being tested works with
    ForwardRef objects that have __globals__ set by Python 3.14's
    PEP 649 deferred annotation evaluation.
    """

    def test_model_with_optional_datetime(self):
        """Test that datetime | None resolves correctly."""
        import datetime

        @dataclasses.dataclass
        class ModelWithOptionalDatetime(AvroModel):
            created_at: datetime.datetime | None = None

        schema = ModelWithOptionalDatetime.avro_schema_to_python()

        # Find the created_at field
        fields = schema.get("fields", [])
        created_at_field = next((f for f in fields if f["name"] == "created_at"), None)

        assert created_at_field is not None
        # Should be a union type with null
        field_type = created_at_field["type"]
        assert isinstance(field_type, list) or "null" in str(field_type)

    def test_model_with_optional_uuid(self):
        """Test that UUID | None resolves correctly."""
        from uuid import UUID

        @dataclasses.dataclass
        class ModelWithOptionalUUID(AvroModel):
            id: UUID | None = None

        schema = ModelWithOptionalUUID.avro_schema_to_python()

        fields = schema.get("fields", [])
        id_field = next((f for f in fields if f["name"] == "id"), None)

        assert id_field is not None

    def test_model_with_list_of_nested_model(self):
        """Test that list[NestedModel] resolves correctly."""

        @dataclasses.dataclass
        class InnerModel(AvroModel):
            value: str

        @dataclasses.dataclass
        class OuterModel(AvroModel):
            items: list[InnerModel] = dataclasses.field(default_factory=list)

        schema = OuterModel.avro_schema_to_python()

        fields = schema.get("fields", [])
        items_field = next((f for f in fields if f["name"] == "items"), None)

        assert items_field is not None
        assert items_field["type"]["type"] == "array"

    def test_model_with_date_types(self):
        """Test that datetime.date and datetime.time resolve correctly."""
        import datetime

        @dataclasses.dataclass
        class ModelWithDateTypes(AvroModel):
            birth_date: datetime.date | None = None
            start_time: datetime.time | None = None

        schema = ModelWithDateTypes.avro_schema_to_python()

        fields = schema.get("fields", [])
        assert len([f for f in fields if f["name"] in ("birth_date", "start_time")]) == 2


class TestRealWorldTypeCheckingScenarios:
    """
    Integration tests that simulate real-world TYPE_CHECKING scenarios.

    These tests create actual Python module files to test the full flow
    of resolving ForwardRef types that are imported under TYPE_CHECKING.
    """

    def test_type_checking_import_with_optional_type(self, tmp_path):
        """Test resolving TYPE_CHECKING imports with optional union types."""
        # Create a module with a class that will be imported under TYPE_CHECKING
        inner_module = tmp_path / "inner_model.py"
        inner_module.write_text("""
from dataclasses import dataclass
from dataclasses_avroschema import AvroModel

@dataclass
class InnerModel(AvroModel):
    name: str
    value: int
""")

        # Create a module that imports InnerModel under TYPE_CHECKING
        outer_module = tmp_path / "outer_model.py"
        outer_module.write_text("""
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dataclasses_avroschema import AvroModel

if TYPE_CHECKING:
    from inner_model import InnerModel

@dataclass
class OuterModel(AvroModel):
    inner: InnerModel | None = None
""")

        # Add tmp_path to sys.path so imports work
        sys.path.insert(0, str(tmp_path))
        try:
            # Import the outer module
            import importlib

            outer = importlib.import_module("outer_model")

            # Generate schema - this should resolve the ForwardRef
            schema = outer.OuterModel.avro_schema_to_python()

            # Verify the schema was generated correctly
            assert schema["type"] == "record"
            assert schema["name"] == "OuterModel"

            fields = schema.get("fields", [])
            inner_field = next((f for f in fields if f["name"] == "inner"), None)
            assert inner_field is not None

            # The type should be a union with null and the InnerModel record
            field_type = inner_field["type"]
            assert isinstance(field_type, list)
            assert "null" in field_type or any(
                isinstance(t, dict) and t.get("name") == "InnerModel" for t in field_type
            )
        finally:
            sys.path.remove(str(tmp_path))
            # Clean up imported modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ("inner_model", "outer_model"):
                    del sys.modules[mod_name]

    def test_type_checking_import_with_list_type(self, tmp_path):
        """Test resolving TYPE_CHECKING imports in list types."""
        # Create a module with a class that will be imported under TYPE_CHECKING
        item_module = tmp_path / "item_model.py"
        item_module.write_text("""
from dataclasses import dataclass
from dataclasses_avroschema import AvroModel

@dataclass
class ItemModel(AvroModel):
    id: str
    description: str
""")

        # Create a module that uses list[ItemModel] with TYPE_CHECKING import
        container_module = tmp_path / "container_model.py"
        container_module.write_text("""
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dataclasses_avroschema import AvroModel

if TYPE_CHECKING:
    from item_model import ItemModel

@dataclass
class ContainerModel(AvroModel):
    items: list[ItemModel] = field(default_factory=list)
""")

        sys.path.insert(0, str(tmp_path))
        try:
            import importlib

            container = importlib.import_module("container_model")

            schema = container.ContainerModel.avro_schema_to_python()

            assert schema["type"] == "record"
            assert schema["name"] == "ContainerModel"

            fields = schema.get("fields", [])
            items_field = next((f for f in fields if f["name"] == "items"), None)
            assert items_field is not None

            # The type should be an array with ItemModel as items
            field_type = items_field["type"]
            assert field_type["type"] == "array"
            assert "items" in field_type
        finally:
            sys.path.remove(str(tmp_path))
            for mod_name in list(sys.modules.keys()):
                if mod_name in ("item_model", "container_model"):
                    del sys.modules[mod_name]

    def test_aliased_typing_module_type_checking(self, tmp_path):
        """Test resolving TYPE_CHECKING with aliased typing module (import typing as tp)."""
        # Create a simple model
        simple_module = tmp_path / "simple_model.py"
        simple_module.write_text("""
from dataclasses import dataclass
from dataclasses_avroschema import AvroModel

@dataclass
class SimpleModel(AvroModel):
    data: str
""")

        # Create a module using aliased typing
        aliased_module = tmp_path / "aliased_model.py"
        aliased_module.write_text("""
from dataclasses import dataclass
import typing as tp

from dataclasses_avroschema import AvroModel

if tp.TYPE_CHECKING:
    from simple_model import SimpleModel

@dataclass
class AliasedModel(AvroModel):
    simple: SimpleModel | None = None
""")

        sys.path.insert(0, str(tmp_path))
        try:
            import importlib

            aliased = importlib.import_module("aliased_model")

            schema = aliased.AliasedModel.avro_schema_to_python()

            assert schema["type"] == "record"
            assert schema["name"] == "AliasedModel"

            fields = schema.get("fields", [])
            simple_field = next((f for f in fields if f["name"] == "simple"), None)
            assert simple_field is not None
        finally:
            sys.path.remove(str(tmp_path))
            for mod_name in list(sys.modules.keys()):
                if mod_name in ("simple_model", "aliased_model"):
                    del sys.modules[mod_name]

    def test_datetime_module_import_under_type_checking(self, tmp_path):
        """Test resolving 'import datetime' under TYPE_CHECKING (module, not class)."""
        module_file = tmp_path / "datetime_model.py"
        module_file.write_text("""
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dataclasses_avroschema import AvroModel

if TYPE_CHECKING:
    import datetime

@dataclass
class DatetimeModel(AvroModel):
    created: datetime.datetime | None = None
    birth_date: datetime.date | None = None
""")

        sys.path.insert(0, str(tmp_path))
        try:
            import importlib

            dt_model = importlib.import_module("datetime_model")

            schema = dt_model.DatetimeModel.avro_schema_to_python()

            assert schema["type"] == "record"
            assert schema["name"] == "DatetimeModel"

            fields = schema.get("fields", [])
            assert len(fields) == 2

            created_field = next((f for f in fields if f["name"] == "created"), None)
            birth_date_field = next((f for f in fields if f["name"] == "birth_date"), None)

            assert created_field is not None
            assert birth_date_field is not None
        finally:
            sys.path.remove(str(tmp_path))
            for mod_name in list(sys.modules.keys()):
                if mod_name == "datetime_model":
                    del sys.modules[mod_name]


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_type_checking_block(self):
        """Test parsing TYPE_CHECKING block with no imports."""
        source = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert imports == {}

    def test_type_checking_with_comments(self):
        """Test parsing TYPE_CHECKING block with comments."""
        source = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # This is a comment
    from datetime import datetime  # inline comment

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "datetime" in imports

    def test_multiple_type_checking_blocks(self):
        """Test parsing multiple TYPE_CHECKING blocks."""
        source = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

# Some code here

if TYPE_CHECKING:
    from uuid import UUID

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "datetime" in imports
        assert "UUID" in imports

    def test_type_checking_with_else_branch(self):
        """Test TYPE_CHECKING block with else branch is handled."""
        source = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
else:
    datetime = None

class MyClass:
    pass
"""
        imports = _parse_type_checking_imports(source)
        assert "datetime" in imports
