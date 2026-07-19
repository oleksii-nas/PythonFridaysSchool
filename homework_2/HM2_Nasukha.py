from datetime import date
import calendar

users = [
    {"name": "Petro Oleksiyovich", "birthday": date(1990, 4, 25)},
    {"name": "Volodya Velik", "birthday": date(1985, 4, 27)},
    {"name": "Zhenya Samokat", "birthday": date(1992, 4, 26)},
]

def _next_birthday(birthday: date, today: date) -> date:
    """Найближча річниця дня народження (29.02 у невисокосний рік → 01.03)."""
    try:
        this_year = birthday.replace(year=today.year)
    except ValueError:
        this_year = date(today.year, 3, 1)
    if this_year >= today:
        return this_year
    try:
        return birthday.replace(year=today.year + 1)
    except ValueError:
        return date(today.year + 1, 3, 1)


def get_birthdays_per_week(users, _today=None):
    today = _today or date.today()

    result = {day: [] for day in calendar.day_name[:5]}

    for user in users:
        name = user["name"]
        birthday = user["birthday"]

        birthday_this_year = _next_birthday(birthday, today)

        delta_days = (birthday_this_year - today).days

        if 0 <= delta_days < 7:
            weekday_index = birthday_this_year.weekday()

            if weekday_index >= 5:
                day_name = "Monday"
            else:
                day_name = calendar.day_name[weekday_index]

            result[day_name].append(name)

    return {day: names for day, names in result.items() if names}


def main():
    result = get_birthdays_per_week(users)
    print(result)


if __name__ == "__main__":
    main()
