from datetime import date
import calendar


def get_birthdays_per_week(users):
    today = date.today()

    # Ініціалізуємо тільки робочі дні
    result = {day: [] for day in calendar.day_name[:5]}

    for name, birthday in users.items():
        birthday_this_year = birthday.replace(year=today.year)

        if birthday_this_year < today:
            birthday_this_year = birthday.replace(year=today.year + 1)

        delta_days = (birthday_this_year - today).days

        if 0 <= delta_days < 7:
            weekday_index = birthday_this_year.weekday()

            # Перенос вихідних
            if weekday_index >= 5:
                day_name = "Monday"
            else:
                day_name = calendar.day_name[weekday_index]

            result[day_name].append(name)

    # Прибираємо порожні дні (якщо потрібно)
    result = {day: names for day, names in result.items() if names}

    return result

users = {  "Petro Oleksiyovich": date(1990, 4, 25), 
           "Volodya Velik": date(1985, 4, 27), 
           "Zhenya Samokat": date(1992, 4, 26), 
        } 
print(get_birthdays_per_week(users))

