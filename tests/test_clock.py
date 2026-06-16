from datetime import datetime, timedelta
from pathlib import Path
import unittest

from alarm_clock_cli.clock import (
    Alarm,
    TIME_FORMAT,
    create_alarm,
    delete_alarm,
    due_alarms,
    load_alarms,
    parse_alarm_time,
    save_alarms,
    snooze_alarm,
    validate_alarm_time,
)


class ClockTests(unittest.TestCase):
    def test_parse_alarm_time(self):
        dt = parse_alarm_time("2026-06-16 18:30")
        self.assertEqual(dt.strftime(TIME_FORMAT), "2026-06-16 18:30")

    def test_save_and_load(self):
        alarm = create_alarm("Tea", datetime.now() + timedelta(minutes=5))
        path = Path(self._testMethodName + ".json")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        save_alarms(path, [alarm])
        self.assertEqual(load_alarms(path), [alarm])

    def test_delete_alarm(self):
        alarm = create_alarm("Tea", datetime.now() + timedelta(minutes=5))
        path = Path(self._testMethodName + ".json")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        save_alarms(path, [alarm])
        self.assertTrue(delete_alarm(path, alarm.id))
        self.assertEqual(load_alarms(path), [])

    def test_due_alarms_filters_fired_items(self):
        now = datetime.now()
        due = create_alarm("Due", now - timedelta(minutes=1))
        future = create_alarm("Later", now + timedelta(minutes=1))
        fired = Alarm(
            id="fired123",
            label="Done",
            time=(now - timedelta(minutes=2)).strftime(TIME_FORMAT),
            created_at=now.strftime(TIME_FORMAT),
            fired_at=now.strftime(TIME_FORMAT),
        )
        alarms = [due, future, fired]
        matches = due_alarms(alarms, now)
        self.assertEqual(matches, [due])

    def test_validate_alarm_time_rejects_past_times(self):
        with self.assertRaises(ValueError):
            validate_alarm_time(datetime.now() - timedelta(minutes=1), datetime.now())

    def test_snooze_alarm_updates_time(self):
        alarm = create_alarm("Tea", datetime.now() + timedelta(minutes=5))
        path = Path(self._testMethodName + ".json")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        save_alarms(path, [alarm])
        snoozed = snooze_alarm(path, alarm.id, minutes=10)
        self.assertIsNotNone(snoozed)
        self.assertEqual(load_alarms(path)[0].id, alarm.id)
        self.assertEqual(load_alarms(path)[0].fired_at, None)


if __name__ == "__main__":
    unittest.main()
