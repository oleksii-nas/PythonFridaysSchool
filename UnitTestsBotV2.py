"""
Unit тести для bot_assistant_v2.py
===================================
Структура:
  TestValidatePhone    — тести validate_phone()
  TestCreateContact    — тести create_contact()
  TestAddPhone         — тести add_phone()
  TestUpdatePhone      — тести update_phone()
  TestSearchContact    — тести search_contact()
  TestRemovePhone      — тести remove_phone()
  TestDeleteContact    — тести delete_contact()
  TestListContacts     — тести list_contacts()
  TestHelloHelp        — тести hello() / show_help()
  TestParseInput       — тести parse_input()

Запуск:
  python -m pytest test_bot_assistant.py -v
  python -m pytest test_bot_assistant.py -v --tb=short
"""

import unittest
import importlib
import sys
import os

# ---------------------------------------------------------------------------
# Підключаємо модуль бота
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
bot = importlib.import_module("bot_assistant_v2")


class BotTestBase(unittest.TestCase):
    """
    Базовий клас для всіх тест-кейсів.
    setUp  — очищає глобальний словник contacts перед кожним тестом.
    tearDown — очищає після кожного тесту.
    Завдяки цьому тести незалежні один від одного.
    """

    def setUp(self) -> None:
        bot.contacts.clear()

    def tearDown(self) -> None:
        bot.contacts.clear()


# ===========================================================================
# 1. validate_phone
# ===========================================================================
class TestValidatePhone(BotTestBase):
    """Тести для validate_phone() — валідація формату номера телефону."""

    # --- Happy path (коректні дані) ---

    def test_valid_digits_only(self) -> None:
        """Номер з тільки цифр — повертає оригінальний рядок."""
        self.assertEqual(bot.validate_phone("0671234567"), "0671234567")

    def test_valid_with_plus(self) -> None:
        """Номер з префіксом '+' — валідний."""
        self.assertEqual(bot.validate_phone("+380671234567"), "+380671234567")

    def test_valid_with_dashes(self) -> None:
        """Номер з дефісами — валідний."""
        self.assertEqual(bot.validate_phone("067-123-45-67"), "067-123-45-67")

    def test_valid_with_spaces(self) -> None:
        """Номер з пробілами — валідний."""
        self.assertEqual(bot.validate_phone("067 123 45 67"), "067 123 45 67")

    def test_valid_minimum_length(self) -> None:
        """Рівно 7 цифр — мінімально допустима довжина."""
        self.assertEqual(bot.validate_phone("1234567"), "1234567")

    # --- Error path (некоректні дані) ---

    def test_invalid_letters(self) -> None:
        """Текст замість номера — ValueError."""
        with self.assertRaises(ValueError):
            bot.validate_phone("abc")

    def test_invalid_mixed(self) -> None:
        """Мікс тексту і цифр — ValueError."""
        with self.assertRaises(ValueError):
            bot.validate_phone("067abc123")

    def test_invalid_too_short(self) -> None:
        """Менше 7 цифр — ValueError."""
        with self.assertRaises(ValueError):
            bot.validate_phone("12345")

    def test_invalid_empty(self) -> None:
        """Порожній рядок — ValueError."""
        with self.assertRaises(ValueError):
            bot.validate_phone("")


# ===========================================================================
# 2. create_contact
# ===========================================================================
class TestCreateContact(BotTestBase):
    """Тести для create_contact() — створення нового контакту."""

    # --- Happy path ---

    def test_create_success(self) -> None:
        """Успішне створення контакту — повідомлення + запис у словник."""
        result = bot.create_contact(["Andrii", "0671234567"])
        self.assertIn("created", result)
        self.assertIn("Andrii", bot.contacts)
        self.assertEqual(bot.contacts["Andrii"], ["0671234567"])

    def test_create_stores_phone_as_list(self) -> None:
        """Телефон зберігається як список (для підтримки кількох номерів)."""
        bot.create_contact(["Maria", "0501234567"])
        self.assertIsInstance(bot.contacts["Maria"], list)

    # --- Edge cases ---

    def test_create_duplicate(self) -> None:
        """Спроба створити вже існуючий контакт — повідомлення про існування."""
        bot.create_contact(["Andrii", "0671234567"])
        result = bot.create_contact(["Andrii", "0991234567"])
        self.assertIn("already exists", result)
        self.assertEqual(len(bot.contacts["Andrii"]), 1)

    # --- Error path ---

    def test_create_invalid_phone(self) -> None:
        """Невалідний телефон — ERR повідомлення, контакт не створюється."""
        result = bot.create_contact(["Andrii", "abc"])
        self.assertIn("ERR", result)
        self.assertNotIn("Andrii", bot.contacts)

    def test_create_missing_phone(self) -> None:
        """Тільки ім'я без телефону — ERR повідомлення."""
        result = bot.create_contact(["Andrii"])
        self.assertIn("ERR", result)

    def test_create_missing_all_args(self) -> None:
        """Порожній список аргументів — ERR повідомлення."""
        result = bot.create_contact([])
        self.assertIn("ERR", result)


# ===========================================================================
# 3. add_phone
# ===========================================================================
class TestAddPhone(BotTestBase):
    """Тести для add_phone() — додавання ще одного номера до контакту."""

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567"]

    # --- Happy path ---

    def test_add_phone_success(self) -> None:
        """Успішне додавання другого номера."""
        result = bot.add_phone(["Andrii", "0991234567"])
        self.assertIn("added", result)
        self.assertIn("0991234567", bot.contacts["Andrii"])
        self.assertEqual(len(bot.contacts["Andrii"]), 2)

    def test_add_multiple_phones(self) -> None:
        """Можна додати більше двох номерів."""
        bot.add_phone(["Andrii", "0991234567"])
        bot.add_phone(["Andrii", "0501234567"])
        self.assertEqual(len(bot.contacts["Andrii"]), 3)

    # --- Edge cases ---

    def test_add_phone_duplicate(self) -> None:
        """Спроба додати вже існуючий номер — повідомлення без зміни списку."""
        result = bot.add_phone(["Andrii", "0671234567"])
        self.assertIn("already exists", result)
        self.assertEqual(len(bot.contacts["Andrii"]), 1)

    # --- Error path ---

    def test_add_phone_contact_not_found(self) -> None:
        """Контакт не існує — ERR повідомлення."""
        result = bot.add_phone(["Petro", "0991234567"])
        self.assertIn("ERR", result)

    def test_add_phone_invalid_phone(self) -> None:
        """Невалідний номер — ERR повідомлення."""
        result = bot.add_phone(["Andrii", "abc"])
        self.assertIn("ERR", result)
        self.assertEqual(len(bot.contacts["Andrii"]), 1)

    def test_add_phone_missing_args(self) -> None:
        """Тільки ім'я без номера — ERR повідомлення."""
        result = bot.add_phone(["Andrii"])
        self.assertIn("ERR", result)


# ===========================================================================
# 4. update_phone
# ===========================================================================
class TestUpdatePhone(BotTestBase):
    """Тести для update_phone() — зміна існуючого номера."""

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567", "0991234567"]

    # --- Happy path ---

    def test_update_success(self) -> None:
        """Успішна зміна номера."""
        result = bot.update_phone(["Andrii", "0671234567", "0660000000"])
        self.assertIn("updated", result)
        self.assertIn("0660000000", bot.contacts["Andrii"])
        self.assertNotIn("0671234567", bot.contacts["Andrii"])

    def test_update_keeps_other_phones(self) -> None:
        """Решта номерів залишаються незміненими."""
        bot.update_phone(["Andrii", "0671234567", "0660000000"])
        self.assertIn("0991234567", bot.contacts["Andrii"])

    # --- Edge cases ---

    def test_update_old_phone_not_found(self) -> None:
        """Старий номер не існує у контакту — повідомлення без змін."""
        result = bot.update_phone(["Andrii", "0000000000", "0660000000"])
        self.assertIn("not found", result)

    # --- Error path ---

    def test_update_contact_not_found(self) -> None:
        """Контакт не існує — ERR повідомлення."""
        result = bot.update_phone(["Petro", "0671234567", "0660000000"])
        self.assertIn("ERR", result)

    def test_update_invalid_new_phone(self) -> None:
        """Новий номер невалідний — ERR повідомлення, старий залишається."""
        result = bot.update_phone(["Andrii", "0671234567", "abc"])
        self.assertIn("ERR", result)
        self.assertIn("0671234567", bot.contacts["Andrii"])

    def test_update_missing_args(self) -> None:
        """Неповні аргументи — ERR повідомлення."""
        result = bot.update_phone(["Andrii", "0671234567"])
        self.assertIn("ERR", result)


# ===========================================================================
# 5. search_contact
# ===========================================================================
class TestSearchContact(BotTestBase):
    """Тести для search_contact() — пошук контакту за іменем."""

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567", "0991234567"]

    # --- Happy path ---

    def test_search_success(self) -> None:
        """Знайдений контакт — повертає ім'я та всі номери."""
        result = bot.search_contact(["Andrii"])
        self.assertIn("Andrii", result)
        self.assertIn("0671234567", result)
        self.assertIn("0991234567", result)

    def test_search_shows_all_phones(self) -> None:
        """Виводяться всі номери з нумерацією."""
        result = bot.search_contact(["Andrii"])
        self.assertIn("1.", result)
        self.assertIn("2.", result)

    # --- Error path ---

    def test_search_not_found(self) -> None:
        """Контакт не існує — ERR повідомлення."""
        result = bot.search_contact(["Petro"])
        self.assertIn("ERR", result)

    def test_search_missing_args(self) -> None:
        """Порожній список аргументів — ERR повідомлення."""
        result = bot.search_contact([])
        self.assertIn("ERR", result)

    def test_search_case_sensitive(self) -> None:
        """Пошук чутливий до регістру — 'andrii' ≠ 'Andrii'."""
        result = bot.search_contact(["andrii"])
        self.assertIn("ERR", result)


# ===========================================================================
# 6. remove_phone
# ===========================================================================
class TestRemovePhone(BotTestBase):
    """Тести для remove_phone() — видалення одного номера з контакту."""

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567", "0991234567"]

    # --- Happy path ---

    def test_remove_one_phone(self) -> None:
        """Видалення одного з двох номерів — контакт залишається."""
        result = bot.remove_phone(["Andrii", "0671234567"])
        self.assertIn("removed", result)
        self.assertNotIn("0671234567", bot.contacts["Andrii"])
        self.assertIn("Andrii", bot.contacts)

    def test_remove_last_phone_deletes_contact(self) -> None:
        """Видалення останнього номера — контакт видаляється повністю."""
        bot.contacts["Andrii"] = ["0671234567"]
        result = bot.remove_phone(["Andrii", "0671234567"])
        self.assertIn("deleted", result)
        self.assertNotIn("Andrii", bot.contacts)

    # --- Edge cases ---

    def test_remove_phone_not_in_contact(self) -> None:
        """Номер не належить контакту — повідомлення без змін."""
        result = bot.remove_phone(["Andrii", "0000000000"])
        self.assertIn("not found", result)
        self.assertEqual(len(bot.contacts["Andrii"]), 2)

    # --- Error path ---

    def test_remove_contact_not_found(self) -> None:
        """Контакт не існує — ERR повідомлення."""
        result = bot.remove_phone(["Petro", "0671234567"])
        self.assertIn("ERR", result)

    def test_remove_missing_args(self) -> None:
        """Тільки ім'я без номера — ERR повідомлення."""
        result = bot.remove_phone(["Andrii"])
        self.assertIn("ERR", result)


# ===========================================================================
# 7. delete_contact
# ===========================================================================
class TestDeleteContact(BotTestBase):
    """Тести для delete_contact() — повне видалення контакту."""

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567"]

    # --- Happy path ---

    def test_delete_success(self) -> None:
        """Успішне видалення — контакт зникає зі словника."""
        result = bot.delete_contact(["Andrii"])
        self.assertIn("deleted", result)
        self.assertNotIn("Andrii", bot.contacts)

    def test_delete_only_target(self) -> None:
        """Видаляється тільки вказаний контакт, інші залишаються."""
        bot.contacts["Maria"] = ["0501234567"]
        bot.delete_contact(["Andrii"])
        self.assertIn("Maria", bot.contacts)

    # --- Error path ---

    def test_delete_not_found(self) -> None:
        """Контакт не існує — ERR повідомлення."""
        result = bot.delete_contact(["Petro"])
        self.assertIn("ERR", result)

    def test_delete_missing_args(self) -> None:
        """Порожній список аргументів — ERR повідомлення."""
        result = bot.delete_contact([])
        self.assertIn("ERR", result)


# ===========================================================================
# 8. list_contacts
# ===========================================================================
class TestListContacts(BotTestBase):
    """Тести для list_contacts() — виведення всіх контактів."""

    # --- Happy path ---

    def test_list_with_contacts(self) -> None:
        """Є контакти — повертає нумерований список."""
        bot.contacts["Andrii"] = ["0671234567"]
        bot.contacts["Maria"]  = ["0501234567"]
        result = bot.list_contacts([])
        self.assertIn("Andrii", result)
        self.assertIn("Maria", result)

    def test_list_shows_multiple_phones(self) -> None:
        """Контакт з кількома номерами — всі показані через '|'."""
        bot.contacts["Andrii"] = ["0671234567", "0991234567"]
        result = bot.list_contacts([])
        self.assertIn("0671234567", result)
        self.assertIn("0991234567", result)
        self.assertIn("|", result)

    # --- Edge cases ---

    def test_list_empty(self) -> None:
        """Словник порожній — повідомлення про відсутність контактів."""
        result = bot.list_contacts([])
        self.assertIn("No contacts", result)


# ===========================================================================
# 9. hello / show_help
# ===========================================================================
class TestHelloHelp(BotTestBase):
    """Тести для hello() та show_help() — привітання і довідка."""

    def test_hello_returns_string(self) -> None:
        """hello() повертає рядок."""
        result = bot.hello([])
        self.assertIsInstance(result, str)

    def test_hello_contains_help_hint(self) -> None:
        """hello() підказує написати 'help'."""
        result = bot.hello([])
        self.assertIn("help", result.lower())

    def test_show_help_returns_help_text(self) -> None:
        """show_help() повертає рядок HELP_TEXT."""
        result = bot.show_help([])
        self.assertEqual(result, bot.HELP_TEXT)

    def test_help_text_contains_all_commands(self) -> None:
        """HELP_TEXT містить назви всіх команд з COMMANDS (крім 'help' — вона викликає саму себе)."""
        excluded = {"help"}
        for cmd in bot.COMMANDS:
            if cmd not in excluded:
                self.assertIn(cmd, bot.HELP_TEXT)


# ===========================================================================
# 10. parse_input
# ===========================================================================
class TestParseInput(BotTestBase):
    """Тести для parse_input() — розбір рядка введення."""

    # --- Happy path ---

    def test_single_command(self) -> None:
        """Одне слово — команда без аргументів."""
        cmd, args = bot.parse_input("hello")
        self.assertEqual(cmd, "hello")
        self.assertEqual(args, [])

    def test_command_with_args(self) -> None:
        """Команда з аргументами — правильний розподіл."""
        cmd, args = bot.parse_input("search Andrii")
        self.assertEqual(cmd, "search")
        self.assertEqual(args, ["Andrii"])

    def test_two_word_command(self) -> None:
        """Двослівна команда розпізнається як єдиний ключ."""
        cmd, args = bot.parse_input("create contact Andrii 0671234567")
        self.assertEqual(cmd, "create contact")
        self.assertEqual(args, ["Andrii", "0671234567"])

    def test_two_word_exit_command(self) -> None:
        """'good bye' розпізнається як команда виходу."""
        cmd, args = bot.parse_input("good bye")
        self.assertEqual(cmd, "good bye")
        self.assertEqual(args, [])

    def test_case_insensitive_command(self) -> None:
        """Команда у верхньому регістрі нормалізується до нижнього."""
        cmd, _ = bot.parse_input("HELLO")
        self.assertEqual(cmd, "hello")

    def test_mixed_case_command(self) -> None:
        """Змішаний регістр команди — нормалізується."""
        cmd, _ = bot.parse_input("Search Andrii")
        self.assertEqual(cmd, "search")

    def test_preserves_args_case(self) -> None:
        """Регістр аргументів (імен) зберігається."""
        _, args = bot.parse_input("search Andrii")
        self.assertEqual(args[0], "Andrii")

    # --- Edge cases ---

    def test_empty_input(self) -> None:
        """Порожній рядок — повертає ('', [])."""
        cmd, args = bot.parse_input("")
        self.assertEqual(cmd, "")
        self.assertEqual(args, [])

    def test_whitespace_only(self) -> None:
        """Рядок тільки з пробілів — повертає ('', [])."""
        cmd, args = bot.parse_input("   ")
        self.assertEqual(cmd, "")
        self.assertEqual(args, [])

    def test_extra_spaces_between_words(self) -> None:
        """Зайві пробіли між словами — ігноруються."""
        cmd, args = bot.parse_input("  search   Andrii  ")
        self.assertEqual(cmd, "search")
        self.assertEqual(args, ["Andrii"])


# ===========================================================================
# Точка входу
# ===========================================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)