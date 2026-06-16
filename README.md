# Alarm Clock CLI

A small Python command-line alarm clock built for a 30-minute engineering exercise.

## What it does

- Add alarms for a specific local date and time
- List saved alarms
- Delete alarms by id
- Snooze a triggered alarm by a few minutes
- Run a foreground watcher that rings when alarms are due
- Persist alarms to a local JSON file, not a database

## Design choices

- **Standard library only**: keeps installation and review simple.
- **JSON persistence**: enough durability for a CLI without introducing a database.
- **Foreground runner**: easy to understand and demo during an interview setting.
- **Input validation**: rejects malformed or past alarm times early.
- **Testable core**: parsing, persistence, and due checks are separated from CLI I/O.

## Install

```bash
python -m pip install -e .
```

## Usage

Add an alarm:

```bash
alarm-clock add --time "2026-06-16 18:30" --label "Wrap up"
```

List alarms:

```bash
alarm-clock list
```

Delete an alarm:

```bash
alarm-clock delete <alarm-id>
```

Snooze an alarm:

```bash
alarm-clock snooze <alarm-id> --minutes 5
```

Run the alarm watcher:

```bash
alarm-clock run
```

## Time format

Use local time in the format `YYYY-MM-DD HH:MM`.
Alarm times must be in the future.

## Storage

Alarms are stored in `~/.alarm_clock_cli/alarms.json` by default.

## Validation

I validated the implementation with unit tests covering time parsing, persistence, and alarm triggering behavior.
