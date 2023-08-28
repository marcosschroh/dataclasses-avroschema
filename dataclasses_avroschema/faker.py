try:
    from faker import Faker

    fake = Faker()
except ImportError:  # pragma: no cover

    class FakeStub:
        """A stub for Faker.fake() when the feature [faker] is not enabled.

        It raises a hard RuntimeError when faker is not installed and
        we tried to invoke `.fake()` on any of our fields.

        We can find the local usages of faker methods (i.e. fake.<method>(*args, **kwargs)) with:

        ```sh
        rg "^.*fake\.(\w+)\(.*\).*$" dataclasses_avroschema -r '$1' -NIo | sort -u
        ```
        """

        def raise_runtime_error(self, *args, **kwargs):
            raise RuntimeError(
                "faker must be installed in order to use .fake(). "
                "Consider running `pip install dataclasses-avroschema[faker]`"
            )

    _FAKER_METHODS_TO_STUB = [
        "company_email",
        "date_object",
        "date_time",
        "first_name",
        "ipv4",
        "last_name",
        "pybool",
        "pydecimal",
        "pyfloat",
        "pyint",
        "pystr",
        "time_object",
        "uri",
        "url",
    ]

    fake = FakeStub()  # type: ignore

    for method in _FAKER_METHODS_TO_STUB:
        setattr(fake, method, fake.raise_runtime_error)
