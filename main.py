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
        while lines[0] != "[Charger Availability Reports]":
            line, lines = lines[0], lines[1:]
            if line == "":
                continue
            station = Station.from_station_line(line)
            print(f"Station {station.id} with chargers {station.charger_ids}")

        lines = lines[1:]  # skip the header line
        for line in lines:
            if line == "":
                continue
            report = UptimeReport.from_report_line(line)
            print(f"Report {report.id} from {report.start_time_nanos} to {report.end_time_nanos}, up: {report.up}")

    return 0

if __name__ == "__main__":
    exit(main())
