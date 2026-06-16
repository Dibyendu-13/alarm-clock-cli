from __future__ import annotations

from argparse import ArgumentParser, Namespace
from datetime import datetime
import sys
import time

from .clock import (
    TIME_FORMAT,
    add_alarm,
    countdown,
    default_store_path,
    delete_alarm,
    due_alarms,
    load_alarms,
    mark_fired,
    parse_alarm_time,
    snooze_alarm,
    validate_alarm_time,
)


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="alarm-clock", description="A simple CLI alarm clock.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add a new alarm")
    add.add_argument("--time", required=True, help='Local time in "YYYY-MM-DD HH:MM" format')
    add.add_argument("--label", default="Alarm", help="Label for the alarm")

    subparsers.add_parser("list", help="List saved alarms")

    delete = subparsers.add_parser("delete", help="Delete an alarm")
    delete.add_argument("alarm_id", help="Alarm id")

    snooze = subparsers.add_parser("snooze", help="Snooze an alarm by 5 minutes")
    snooze.add_argument("alarm_id", help="Alarm id")
    snooze.add_argument("--minutes", type=int, default=5, help="Minutes to snooze")

    subparsers.add_parser("run", help="Watch for due alarms")
    return parser


def format_alarm_line(alarm) -> str:
    status = "fired" if alarm.fired_at else "pending"
    return f"{alarm.id} | {alarm.time} | {alarm.label} | {status}"


def cmd_add(args: Namespace) -> int:
    try:
        when = parse_alarm_time(args.time)
        validate_alarm_time(when)
    except ValueError as exc:
        print(f"Invalid alarm time: {exc}", file=sys.stderr)
        return 1
    alarm = add_alarm(default_store_path(), args.label, when)
    print(f"Added alarm {alarm.id} for {alarm.time} ({alarm.label})")
    return 0


def cmd_list(_: Namespace) -> int:
    alarms = load_alarms(default_store_path())
    if not alarms:
        print("No alarms saved.")
        return 0
    for alarm in sorted(alarms, key=lambda item: item.time):
        print(format_alarm_line(alarm))
    return 0


def cmd_delete(args: Namespace) -> int:
    removed = delete_alarm(default_store_path(), args.alarm_id)
    if not removed:
        print(f"No alarm found with id {args.alarm_id}", file=sys.stderr)
        return 1
    print(f"Deleted alarm {args.alarm_id}")
    return 0


def cmd_snooze(args: Namespace) -> int:
    alarm = snooze_alarm(default_store_path(), args.alarm_id, args.minutes)
    if alarm is None:
        print(f"No alarm found with id {args.alarm_id}", file=sys.stderr)
        return 1
    print(f"Snoozed alarm {alarm.id} to {alarm.time}")
    return 0


def cmd_run(_: Namespace) -> int:
    path = default_store_path()
    print("Watching for alarms. Press Ctrl+C to stop.")
    try:
        while True:
            alarms = load_alarms(path)
            due = due_alarms(alarms, datetime.now())
            for alarm in due:
                print("\a")
                print(f"ALARM: {alarm.label} at {alarm.time}")
                mark_fired(path, alarm.id)
            pending = [alarm for alarm in alarms if alarm.fired_at is None]
            next_alarm = min(pending, key=lambda alarm: alarm.scheduled_for, default=None)
            if next_alarm:
                remaining = countdown(next_alarm.scheduled_for)
                print(f"Next alarm in {int(remaining.total_seconds())}s", end="\r")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "add":
        return cmd_add(args)
    if args.command == "list":
        return cmd_list(args)
    if args.command == "delete":
        return cmd_delete(args)
    if args.command == "snooze":
        return cmd_snooze(args)
    if args.command == "run":
        return cmd_run(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
