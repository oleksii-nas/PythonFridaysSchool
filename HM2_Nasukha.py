from datetime import date
import calendar

users = [
    {"name": "Petro Oleksiyovich", "birthday": date(1990, 4, 25)},
    {"name": "Volodya Velik", "birthday": date(1985, 4, 27)},
    {"name": "Zhenya Samokat", "birthday": date(1992, 4, 26)},
]

def get_birthdays_per_week(users):
    today = date.today()

    result = {day: [] for day in calendar.day_name[:5]}

    for user in users:
        name = user["name"]
        birthday = user["birthday"]

        birthday_this_year = birthday.replace(year=today.year)

        if birthday_this_year < today:
            birthday_this_year = birthday.replace(year=today.year + 1)

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
    print(get_birthdays_per_week(users))
