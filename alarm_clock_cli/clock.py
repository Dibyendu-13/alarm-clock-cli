from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json
import uuid


TIME_FORMAT = "%Y-%m-%d %H:%M"


@dataclass(frozen=True)
class Alarm:
    id: str
    label: str
    time: str
    created_at: str
    fired_at: str | None = None

    @property
    def scheduled_for(self) -> datetime:
        return datetime.strptime(self.time, TIME_FORMAT)

    @property
    def is_due(self) -> bool:
        return datetime.now() >= self.scheduled_for


def parse_alarm_time(raw: str) -> datetime:
    return datetime.strptime(raw, TIME_FORMAT)


def validate_alarm_time(when: datetime, now: datetime | None = None) -> None:
    current = now or datetime.now()
    if when <= current:
        raise ValueError("Alarm time must be in the future.")


def create_alarm(label: str, when: datetime) -> Alarm:
    now = datetime.now().replace(microsecond=0)
    return Alarm(
        id=str(uuid.uuid4())[:8],
        label=label.strip() or "Alarm",
        time=when.replace(microsecond=0).strftime(TIME_FORMAT),
        created_at=now.strftime(TIME_FORMAT),
    )


def default_store_path() -> Path:
    return Path.home() / ".alarm_clock_cli" / "alarms.json"


def load_alarms(path: Path) -> list[Alarm]:
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return [Alarm(**item) for item in data]


def save_alarms(path: Path, alarms: list[Alarm]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(alarm) for alarm in alarms]
    path.write_text(json.dumps(payload, indent=2))


def add_alarm(path: Path, label: str, when: datetime) -> Alarm:
    validate_alarm_time(when)
    alarms = load_alarms(path)
    alarm = create_alarm(label, when)
    alarms.append(alarm)
    save_alarms(path, alarms)
    return alarm


def delete_alarm(path: Path, alarm_id: str) -> bool:
    alarms = load_alarms(path)
    updated = [alarm for alarm in alarms if alarm.id != alarm_id]
    if len(updated) == len(alarms):
        return False
    save_alarms(path, updated)
    return True


def mark_fired(path: Path, alarm_id: str) -> None:
    alarms = load_alarms(path)
    updated = []
    fired_at = datetime.now().replace(microsecond=0).strftime(TIME_FORMAT)
    for alarm in alarms:
        if alarm.id == alarm_id:
            updated.append(
                Alarm(
                    id=alarm.id,
                    label=alarm.label,
                    time=alarm.time,
                    created_at=alarm.created_at,
                    fired_at=fired_at,
                )
            )
        else:
            updated.append(alarm)
    save_alarms(path, updated)


def snooze_alarm(path: Path, alarm_id: str, minutes: int = 5) -> Alarm | None:
    alarms = load_alarms(path)
    updated = []
    snoozed_alarm = None
    for alarm in alarms:
        if alarm.id == alarm_id:
            base_time = alarm.scheduled_for if alarm.fired_at is None else datetime.now()
            new_time = (base_time + timedelta(minutes=minutes)).replace(microsecond=0)
            snoozed_alarm = Alarm(
                id=alarm.id,
                label=alarm.label,
                time=new_time.strftime(TIME_FORMAT),
                created_at=alarm.created_at,
                fired_at=None,
            )
            updated.append(snoozed_alarm)
        else:
            updated.append(alarm)
    if snoozed_alarm is None:
        return None
    save_alarms(path, updated)
    return snoozed_alarm


def due_alarms(alarms: list[Alarm], now: datetime | None = None) -> list[Alarm]:
    current = now or datetime.now()
    return [alarm for alarm in alarms if current >= alarm.scheduled_for and alarm.fired_at is None]


def countdown(target: datetime, now: datetime | None = None) -> timedelta:
    current = now or datetime.now()
    return max(target - current, timedelta(0))
