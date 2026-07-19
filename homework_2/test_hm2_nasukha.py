"""
Unit тести для HM2_Nasukha.py — пошук днів народжень на найближчий тиждень.

Дати будуються динамічно відносно date.today(), тож тести
не залежать від конкретної дати запуску.

Запуск:
  python -m pytest homework_2 -v
"""

import calendar
import importlib
import os
import sys
import unittest
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
bd = importlib.import_module("HM2_Nasukha")


def next_weekday(weekday: int) -> date:
    """Найближча дата (включно з сьогодні) із заданим днем тижня, у межах 7 днів."""
    today = date.today()
    offset = (weekday - today.weekday()) % 7
    return today + timedelta(days=offset)


class TestGetBirthdaysPerWeek(unittest.TestCase):
    def test_birthday_today_is_included(self) -> None:
        today = date.today()
        users = [{"name": "Today Person", "birthday": today}]
        result = bd.get_birthdays_per_week(users)
        names = [name for day in result.values() for name in day]
        self.assertIn("Today Person", names)

    def test_weekday_birthday_lands_on_its_day(self) -> None:
        wednesday = next_weekday(2)  # 2 == Wednesday
        users = [{"name": "Wed Person", "birthday": wednesday}]
        result = bd.get_birthdays_per_week(users)
        self.assertIn("Wed Person", result.get("Wednesday", []))

    def test_saturday_birthday_shifts_to_monday(self) -> None:
        saturday = next_weekday(5)  # 5 == Saturday
        users = [{"name": "Sat Person", "birthday": saturday}]
        result = bd.get_birthdays_per_week(users)
        self.assertIn("Sat Person", result.get("Monday", []))

    def test_sunday_birthday_shifts_to_monday(self) -> None:
        sunday = next_weekday(6)  # 6 == Sunday
        users = [{"name": "Sun Person", "birthday": sunday}]
        result = bd.get_birthdays_per_week(users)
        self.assertIn("Sun Person", result.get("Monday", []))

    def test_birthday_beyond_week_is_excluded(self) -> None:
        far = date.today() + timedelta(days=10)
        users = [{"name": "Far Person", "birthday": far}]
        result = bd.get_birthdays_per_week(users)
        names = [name for day in result.values() for name in day]
        self.assertNotIn("Far Person", names)

    def test_empty_users_returns_empty_dict(self) -> None:
        self.assertEqual(bd.get_birthdays_per_week([]), {})

    def test_result_has_no_empty_days(self) -> None:
        users = [{"name": "Only One", "birthday": next_weekday(2)}]
        result = bd.get_birthdays_per_week(users)
        for names in result.values():
            self.assertTrue(names)

    def test_only_weekday_names_as_keys(self) -> None:
        allowed = set(calendar.day_name[:5])  # Monday..Friday
        users = [{"name": "P", "birthday": next_weekday(5)}]
        result = bd.get_birthdays_per_week(users)
        self.assertTrue(set(result.keys()).issubset(allowed))

    def test_feb29_birthday_does_not_crash_in_nonleap_year(self) -> None:
        users = [{"name": "Leap Person", "birthday": date(1992, 2, 29)}]
        # 2026 — невисокосний рік; 29.02 трактується як 01.03
        result = bd.get_birthdays_per_week(users, _today=date(2026, 2, 26))
        names = [name for day in result.values() for name in day]
        self.assertIn("Leap Person", names)

    def test_feb29_birthday_far_from_march_is_excluded(self) -> None:
        users = [{"name": "Leap Person", "birthday": date(1992, 2, 29)}]
        result = bd.get_birthdays_per_week(users, _today=date(2026, 7, 15))
        names = [name for day in result.values() for name in day]
        self.assertNotIn("Leap Person", names)

    def test_boundary_six_days_ahead_included(self) -> None:
        today = date(2026, 7, 15)  # середа
        users = [{"name": "Edge In", "birthday": today + timedelta(days=6)}]
        result = bd.get_birthdays_per_week(users, _today=today)
        names = [name for day in result.values() for name in day]
        self.assertIn("Edge In", names)

    def test_boundary_seven_days_ahead_excluded(self) -> None:
        today = date(2026, 7, 15)
        users = [{"name": "Edge Out", "birthday": today + timedelta(days=7)}]
        result = bd.get_birthdays_per_week(users, _today=today)
        names = [name for day in result.values() for name in day]
        self.assertNotIn("Edge Out", names)

    def test_multiple_users_same_day_grouped(self) -> None:
        wednesday = next_weekday(2)
        users = [
            {"name": "First", "birthday": wednesday},
            {"name": "Second", "birthday": wednesday},
        ]
        result = bd.get_birthdays_per_week(users)
        self.assertEqual(len(result.get("Wednesday", [])), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)