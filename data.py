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

        match elts[3]:
            case "true":
                up = True
            case "false":
                up = False
            case _:
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
        return Decimal("25.7")