from dataclasses import dataclass
from data import UptimeReport, Station
from contextlib import AbstractContextManager, nullcontext as does_not_raise
import pytest

@dataclass
class UptimeReportTestCase:
    line: str
    want_report: UptimeReport | None
    expectation: AbstractContextManager

uptime_report_test_cases: dict[str, UptimeReportTestCase] = {
    "no_error": UptimeReportTestCase(
        line="1001 0 50000 true",
        want_report=UptimeReport(
            id="1001",
            start_time_nanos=0,
            end_time_nanos=50000,
            up=True,
        ),
        expectation=does_not_raise(),
    ),
    "three_elements_invalid": UptimeReportTestCase(
        line="1001 0 50000",
        want_report=None,
        expectation=pytest.raises(ValueError),
    ),
    "five_elements_invalid": UptimeReportTestCase(
        line="1001 0 50000 false extra",
        want_report=None,
        expectation=pytest.raises(ValueError),
    ),
    "non_numeric_start": UptimeReportTestCase(
        line="1001 0x 50000 true",
        want_report=None,
        expectation=pytest.raises(ValueError),
    ),
    "unrecognized_bool_value": UptimeReportTestCase(
        line="1001 0 50000 not_a_bool",
        want_report=None,
        expectation=pytest.raises(ValueError),
    ),
}
test_ids = sorted(uptime_report_test_cases.keys())
@pytest.mark.parametrize(
    "test_case",
    [uptime_report_test_cases[test_id] for test_id in test_ids],
    ids=test_ids,
)
def test_uptime_report_from_report_line(test_case: UptimeReportTestCase) -> None:
    with test_case.expectation:
        report = UptimeReport.from_report_line(test_case.line)
        assert report == test_case.want_report


@dataclass
class StationTestCase:
    line: str
    want_station: Station | None
    expectation: AbstractContextManager

station_test_cases: dict[str, StationTestCase] = {
    "valid_station": StationTestCase(
        line="0 1001 1002",
        want_station=Station(
            id="0",
            charger_ids=["1001", "1002"],
        ),
        expectation=does_not_raise(),
    ),
    "no_chargers": StationTestCase(
        line="station1",
        want_station=None,
        expectation=pytest.raises(ValueError),
    ),
}
test_ids = sorted(station_test_cases.keys())
@pytest.mark.parametrize(
    "test_case",
    [station_test_cases[test_id] for test_id in test_ids],
    ids=test_ids,
)
def test_station_from_station_line(test_case: StationTestCase) -> None:
    with test_case.expectation:
        station = Station.from_station_line(test_case.line)
        assert station == test_case.want_station