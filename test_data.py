from dataclasses import dataclass
from data import UptimeReport, Station
from contextlib import AbstractContextManager, nullcontext as does_not_raise
import pytest
from decimal import Decimal

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


@dataclass
class StationUptimeTestCase:
    station: Station
    reports_per_charger: dict[str, list[UptimeReport]]
    want_uptime: Decimal
station_uptime_test_cases: dict[str, StationUptimeTestCase] = {
    "basic_case": StationUptimeTestCase(
        station=Station(id="0", charger_ids=["1001", "1002"]),
        reports_per_charger={
            "1001": [
                UptimeReport(id="1001", start_time_nanos=0, end_time_nanos=50000, up=True),
                UptimeReport(id="1001", start_time_nanos=50000, end_time_nanos=100000, up=False),
            ],
            "1002": [
                UptimeReport(id="1002", start_time_nanos=50000, end_time_nanos=100000, up=True),
            ],
        },
        want_uptime=Decimal("100.0"),
    ),
    "explicit_downtime": StationUptimeTestCase(
        station=Station(id="1", charger_ids=["1003"]),
        reports_per_charger={
            "1003": [
                UptimeReport(id="1003", start_time_nanos=25000, end_time_nanos=75000, up=False),
            ],
        },
        want_uptime=Decimal("0.0"),
    ),
    "gap_is_downtime": StationUptimeTestCase(
        station=Station(id="2", charger_ids=["1004"]),
        reports_per_charger={
            "1004": [
                UptimeReport(id="1004", start_time_nanos=0, end_time_nanos=50000, up=True),
                UptimeReport(id="1004", start_time_nanos=100000, end_time_nanos=200000, up=True),
            ],
        },
        want_uptime=Decimal("75.0"),
    ),
    "input2_station0": StationUptimeTestCase(
        station=Station(id="0", charger_ids=["0"]),
        reports_per_charger={
            "0": [
                UptimeReport(id="0", start_time_nanos=10, end_time_nanos=20, up=True),
                UptimeReport(id="0", start_time_nanos=20, end_time_nanos=30, up=False),
                UptimeReport(id="0", start_time_nanos=30, end_time_nanos=40, up=True),
            ],
        },
        want_uptime=Decimal("2") / Decimal("3") * Decimal("100.0"),
    ),
}
test_ids = sorted(station_uptime_test_cases.keys())
@pytest.mark.parametrize(
    "test_case",
    [station_uptime_test_cases[test_id] for test_id in test_ids],
    ids=test_ids,
)
def test_station_compute_uptime(test_case: StationUptimeTestCase) -> None:
    uptime = test_case.station.compute_uptime(test_case.reports_per_charger)
    assert uptime == test_case.want_uptime