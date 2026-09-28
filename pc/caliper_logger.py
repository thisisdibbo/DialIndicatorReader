#!/usr/bin/env python3
"""Log readings from DialIndicatorReader to the screen and (optionally) a CSV.

    python caliper_logger.py --list
    python caliper_logger.py --port COM5
    python caliper_logger.py --port COM5 --csv run1.csv

Author: Md. Mahin Rahman <mr.d2003feb@gmail.com>  -  https://github.com/thisisdibbo
MIT License - see LICENSE.
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial is missing.  Install it with:  pip install pyserial")

# Matches "10.01 mm", "0.3940 in" and bare numbers like "10.01".
READING = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*(mm|in)?\s*$")


def show_ports():
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return
    for p in ports:
        print(f"{p.device:10s} {p.description}")


def parse(line, default_unit):
    match = READING.match(line)
    if not match:
        return None
    value, unit = match.groups()
    return float(value), (unit or default_unit)


def main():
    ap = argparse.ArgumentParser(description="DialIndicatorReader serial logger")
    ap.add_argument("--port", help="serial port, e.g. COM5 or /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--csv", help="append readings to this CSV file")
    ap.add_argument("--unit", default="mm", help="unit to assume if the sketch "
                    "prints bare numbers (default: mm)")
    ap.add_argument("--list", action="store_true", help="list serial ports and exit")
    args = ap.parse_args()

    if args.list:
        show_ports()
        return
    if not args.port:
        ap.error("--port is required (use --list to see what is available)")

    writer = None
    csv_file = None
    if args.csv:
        needs_header = not os.path.exists(args.csv) or os.path.getsize(args.csv) == 0
        csv_file = open(args.csv, "a", newline="")
        writer = csv.writer(csv_file)
        if needs_header:
            writer.writerow(["timestamp", "value", "unit"])

    print(f"Reading {args.port} at {args.baud} baud.  Ctrl+C to stop.")
    try:
        with serial.Serial(args.port, args.baud, timeout=2) as port:
            while True:
                raw = port.readline().decode("ascii", "ignore").strip()
                if not raw:
                    continue
                reading = parse(raw, args.unit)
                if reading is None:
                    continue
                value, unit = reading
                stamp = datetime.now().isoformat(timespec="milliseconds")
                print(f"{stamp}  {value:>10.4f} {unit}")
                if writer:
                    writer.writerow([stamp, value, unit])
                    csv_file.flush()
    except KeyboardInterrupt:
        print("\nStopped.")
    except serial.SerialException as exc:
        sys.exit(f"Serial error: {exc}")
    finally:
        if csv_file:
            csv_file.close()


if __name__ == "__main__":
    main()
