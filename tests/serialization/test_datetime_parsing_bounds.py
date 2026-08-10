import datetime
import typing
from dataclasses import dataclass

import pytest

from dataclasses_avroschema import AvroModel, dacite_config


def test_ordinary_values_still_parse() -> None:
    assert dacite_config.parse_datetime("2024-10-12T17:57:42+00:00") == datetime.datetime(
        2024, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc
    )
    assert dacite_config.parse_date("2024-10-12") == datetime.date(2024, 10, 12)
    assert dacite_config.parse_time("17:57:42") == datetime.time(17, 57, 42)


def test_values_that_are_already_parsed_are_left_alone() -> None:
    now = datetime.datetime(2024, 10, 12, 17, 57, 42)

    assert dacite_config.parse_datetime(now) is now
    assert dacite_config.parse_date(now.date()) == now.date()
    assert dacite_config.parse_time(now.time()) == now.time()


@pytest.mark.parametrize("parse", [dacite_config.parse_datetime, dacite_config.parse_date, dacite_config.parse_time])
def test_an_overlong_value_is_refused_before_it_is_parsed(parse: typing.Callable) -> None:
    value = "1 " * dacite_config.MAX_DATETIME_STRING_LENGTH

    with pytest.raises(ValueError, match="above the maximum"):
        parse(value)


def test_a_value_at_the_maximum_is_still_parsed() -> None:
    value = "2024-10-12T17:57:42+00:00".ljust(dacite_config.MAX_DATETIME_STRING_LENGTH)

    assert dacite_config.parse_datetime(value) == datetime.datetime(
        2024, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc
    )


def test_parse_obj_refuses_an_overlong_timestamp() -> None:
    @dataclass
    class Event(AvroModel):
        created_at: datetime.datetime

    with pytest.raises(ValueError, match="above the maximum"):
        Event.parse_obj({"created_at": "1 " * dacite_config.MAX_DATETIME_STRING_LENGTH})


def test_a_project_can_supply_its_own_hooks() -> None:
    """The limit is a default, not a decision taken away from the caller: `Meta.dacite_config`
    already replaces the type hooks."""
    fixed = datetime.datetime(2000, 1, 1)

    @dataclass
    class Event(AvroModel):
        created_at: datetime.datetime

        class Meta:
            dacite_config = {"type_hooks": {datetime.datetime: lambda value: fixed}}

    assert Event.parse_obj({"created_at": "1 " * dacite_config.MAX_DATETIME_STRING_LENGTH}).created_at == fixed
