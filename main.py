#!/usr/bin/python3

import argparse

from data import Station, UptimeReport

def main() -> int:
    parser = argparse.ArgumentParser(description="Charger Uptime Report")
    parser.add_argument("filename")
    args = parser.parse_args()

    print(f"in main {args.filename=}")

    with open(args.filename, "r") as file:
        lines = [l.strip() for l in file.readlines()]
        # for idx, line in enumerate(lines):
        #     print(f"{idx}: {line()}")

        # drop any leading empty lines
        while lines[0] == "":
            lines = lines[1:]
        
        if lines[0] != "[Stations]":
            raise ValueError("expected [Stations] at the start of the file")
        
        lines = lines[1:]  # skip the header line
        stations: list[Station] = []
        while lines[0] != "[Charger Availability Reports]":
            line, lines = lines[0], lines[1:]
            if line == "":
                continue
            station = Station.from_station_line(line)
            print(f"Station {station.id} with chargers {station.charger_ids}")
            stations.append(station)


        lines = lines[1:]  # skip the header line
        reports: list[UptimeReport] = []
        for line in lines:
            if line == "":
                continue
            report = UptimeReport.from_report_line(line)
            print(f"Report {report.id} from {report.start_time_nanos} to {report.end_time_nanos}, up: {report.up}")
            reports.append(report)
        reports_per_charger: dict[str, list[UptimeReport]] = {}
        for report in reports:
            if report.id not in reports_per_charger:
                reports_per_charger[report.id] = []
            reports_per_charger[report.id].append(report)
        for charger, reports in reports_per_charger.items():
            print(f"Charger {charger}")
            for report in reports_per_charger[charger]:
                print(f"  {report.start_time_nanos} to {report.end_time_nanos}, up: {report.up}")


    return 0

if __name__ == "__main__":
    exit(main())
