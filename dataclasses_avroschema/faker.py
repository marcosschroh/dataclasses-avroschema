try:
    from faker import Faker

    fake = Faker()
except ModuleNotFoundError:  # pragma: no cover

    class FakeStub:
        """A stub for Faker.fake() when the feature [faker] is not enabled.
        It raises a hard RuntimeError when faker is not installed and
        we tried to invoke `.fake()` on any of our fields.
        We can find the local usages of faker methods (i.e. fake.<method>(*args, **kwargs)) with:
        ```sh
        rg "^.*fake\.(\w+)\(.*\).*$" dataclasses_avroschema -r '$1' -NIo | sort -u
        ```
        """

        def __getattr__(self, item):
            raise RuntimeError(
                "faker must be installed in order to use .fake(). "
                "Consider running `pip install dataclasses-avroschema[faker]`"
            )

    fake = FakeStub()  # type: ignore
