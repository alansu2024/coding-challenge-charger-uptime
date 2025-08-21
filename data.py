from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class UptimeReport:
    id: str
    start_time_nanos: int
    end_time_nanos: int
    up: bool

    @staticmethod
    def from_report_line(line: str) -> UptimeReport:
        elts: list[str] = line.split(" ")
        if len(elts) != 4:
            raise ValueError(f"failed to parse report line: {line}")

        if elts[3] == "true":
            up = True
        elif elts[3] == "false":
            up = False
        else:
            raise ValueError(f"invalid up value {elts[3]}")

        return UptimeReport(
            id=elts[0],
            start_time_nanos=int(elts[1]),
            end_time_nanos=int(elts[2]),
            up=up,
        )

@dataclass
class Charger:
    id: str
    uptime_reports: list[UptimeReport]

@dataclass
class Station:
    id: str
    charger_ids: list[str]

    @staticmethod
    def from_station_line(line: str) -> Station:
        elts: list[str] = line.split(" ")
        if len(elts) < 2:
            raise ValueError(f"failed to parse station line: {line}")

        return Station(
            id=elts[0],
            charger_ids=elts[1:],
        )

    def compute_uptime(self, reports_per_charger: dict[str, list[UptimeReport]]) -> Decimal:
        charger_reports = []
        for charger_id in self.charger_ids:
            charger_reports.append(reports_per_charger.get(charger_id, []))

        max_end_time = max(
            (report.end_time_nanos for reports in charger_reports for report in reports),
            default=0,
        )
        assert max_end_time > 0, "no reports found for this station"

        min_start_time = min(
            (report.start_time_nanos for reports in charger_reports for report in reports),
            default=0,
        )
        cur_time = min_start_time
        down_time = 0
        cur_indices = [0] * len(charger_reports)
        while cur_time < max_end_time:
            # see if any charger is up
            def _up(idx: int) -> bool:
                return (
                    cur_indices[idx] < len(charger_reports[idx])
                    and cur_time >= charger_reports[idx][cur_indices[idx]].start_time_nanos
                    and charger_reports[idx][cur_indices[idx]].up
                )
            up = any([_up(idx) for idx in range(len(charger_reports))])
            # print(f"{up=} @{cur_time}")

            # the next time is the min of hte next end time
            def _next_time(idx: int) -> int | None:
                if cur_indices[idx] == len(charger_reports[idx]):
                    return None
                # if the current time is before the current index, then return the start time
                if cur_time < charger_reports[idx][cur_indices[idx]].start_time_nanos:
                    return charger_reports[idx][cur_indices[idx]].start_time_nanos
                return charger_reports[idx][cur_indices[idx]].end_time_nanos
            next_times = [_next_time(idx) for idx in range(len(charger_reports))]
            next_time = min([t for t in next_times if t is not None])
            if not up:
                down_time += next_time - cur_time
            cur_time = next_time

            # increment the indices for any charger where the current index is now beyond that
            # report's end time
            for idx in range(len(charger_reports)):
                if cur_indices[idx] < len(charger_reports[idx]) and cur_time >= charger_reports[idx][cur_indices[idx]].end_time_nanos:
                    cur_indices[idx] += 1

        return Decimal(max_end_time - min_start_time - down_time) / Decimal(max_end_time - min_start_time) * Decimal(100.0)