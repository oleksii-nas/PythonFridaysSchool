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
bot = importlib.import_module("HW_3_Nasukha")


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

    def test_valid_digits_only(self) -> None:
        phone = "0671234567"
        result = bot.validate_phone(phone)
        print(f"\n  input:  '{phone}' -> result: '{result}'")
        self.assertEqual(result, phone)

    def test_valid_with_plus(self) -> None:
        phone = "+380671234567"
        result = bot.validate_phone(phone)
        print(f"\n  input:  '{phone}' -> result: '{result}'")
        self.assertEqual(result, phone)

    def test_valid_with_dashes(self) -> None:
        phone = "067-123-45-67"
        result = bot.validate_phone(phone)
        print(f"\n  input:  '{phone}' -> result: '{result}'")
        self.assertEqual(result, phone)

    def test_valid_with_spaces(self) -> None:
        phone = "067 123 45 67"
        result = bot.validate_phone(phone)
        print(f"\n  input:  '{phone}' -> result: '{result}'")
        self.assertEqual(result, phone)

    def test_valid_minimum_length(self) -> None:
        phone = "1234567"
        result = bot.validate_phone(phone)
        print(f"\n  input:  '{phone}' -> result: '{result}'")
        self.assertEqual(result, phone)

    def test_invalid_letters(self) -> None:
        phone = "abc"
        print(f"\n  input:  '{phone}' -> expected: ValueError")
        with self.assertRaises(ValueError) as ctx:
            bot.validate_phone(phone)
        print(f"  raised: ValueError('{ctx.exception}')")

    def test_invalid_mixed(self) -> None:
        phone = "067abc123"
        print(f"\n  input:  '{phone}' -> expected: ValueError")
        with self.assertRaises(ValueError) as ctx:
            bot.validate_phone(phone)
        print(f"  raised: ValueError('{ctx.exception}')")

    def test_invalid_too_short(self) -> None:
        phone = "12345"
        print(f"\n  input:  '{phone}' -> expected: ValueError")
        with self.assertRaises(ValueError) as ctx:
            bot.validate_phone(phone)
        print(f"  raised: ValueError('{ctx.exception}')")

    def test_invalid_empty(self) -> None:
        phone = ""
        print(f"\n  input:  '{phone}' -> expected: ValueError")
        with self.assertRaises(ValueError) as ctx:
            bot.validate_phone(phone)
        print(f"  raised: ValueError('{ctx.exception}')")


# ===========================================================================
# 2. create_contact
# ===========================================================================
class TestCreateContact(BotTestBase):

    def test_create_success(self) -> None:
        args = ["Andrii", "0671234567"]
        result = bot.create_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        print(f"  contacts: {dict(bot.contacts)}")
        self.assertIn("created", result)
        self.assertIn("Andrii", bot.contacts)
        self.assertEqual(bot.contacts["Andrii"], ["0671234567"])

    def test_create_stores_phone_as_list(self) -> None:
        args = ["Maria", "0501234567"]
        bot.create_contact(args)
        print(f"\n  input:   {args}")
        print(f"  contacts['Maria'] type: {type(bot.contacts['Maria']).__name__} = {bot.contacts['Maria']}")
        self.assertIsInstance(bot.contacts["Maria"], list)

    def test_create_duplicate(self) -> None:
        bot.create_contact(["Andrii", "0671234567"])
        args = ["Andrii", "0991234567"]
        result = bot.create_contact(args)
        print(f"\n  input:   {args} (Andrii already exists)")
        print(f"  result:  '{result}'")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertIn("already exists", result)
        self.assertEqual(len(bot.contacts["Andrii"]), 1)

    def test_create_invalid_phone(self) -> None:
        args = ["Andrii", "abc"]
        result = bot.create_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        print(f"  'Andrii' in contacts: {'Andrii' in bot.contacts}")
        self.assertIn("ERR", result)
        self.assertNotIn("Andrii", bot.contacts)

    def test_create_missing_phone(self) -> None:
        args = ["Andrii"]
        result = bot.create_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)

    def test_create_missing_all_args(self) -> None:
        args = []
        result = bot.create_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)


# ===========================================================================
# 3. add_phone
# ===========================================================================
class TestAddPhone(BotTestBase):

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567"]

    def test_add_phone_success(self) -> None:
        args = ["Andrii", "0991234567"]
        result = bot.add_phone(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertIn("added", result)
        self.assertIn("0991234567", bot.contacts["Andrii"])
        self.assertEqual(len(bot.contacts["Andrii"]), 2)

    def test_add_multiple_phones(self) -> None:
        bot.add_phone(["Andrii", "0991234567"])
        bot.add_phone(["Andrii", "0501234567"])
        print(f"\n  added 2 extra phones")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertEqual(len(bot.contacts["Andrii"]), 3)

    def test_add_phone_duplicate(self) -> None:
        args = ["Andrii", "0671234567"]
        result = bot.add_phone(args)
        print(f"\n  input:   {args} (phone already exists)")
        print(f"  result:  '{result}'")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertIn("already exists", result)
        self.assertEqual(len(bot.contacts["Andrii"]), 1)

    def test_add_phone_contact_not_found(self) -> None:
        args = ["Petro", "0991234567"]
        result = bot.add_phone(args)
        print(f"\n  input:   {args} (contact does not exist)")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)

    def test_add_phone_invalid_phone(self) -> None:
        args = ["Andrii", "abc"]
        result = bot.add_phone(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertIn("ERR", result)
        self.assertEqual(len(bot.contacts["Andrii"]), 1)

    def test_add_phone_missing_args(self) -> None:
        args = ["Andrii"]
        result = bot.add_phone(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)


# ===========================================================================
# 4. update_phone
# ===========================================================================
class TestUpdatePhone(BotTestBase):

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567", "0991234567"]

    def test_update_success(self) -> None:
        args = ["Andrii", "0671234567", "0660000000"]
        result = bot.update_phone(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertIn("updated", result)
        self.assertIn("0660000000", bot.contacts["Andrii"])
        self.assertNotIn("0671234567", bot.contacts["Andrii"])

    def test_update_keeps_other_phones(self) -> None:
        args = ["Andrii", "0671234567", "0660000000"]
        bot.update_phone(args)
        print(f"\n  input:   {args}")
        print(f"  contacts['Andrii'] after update: {bot.contacts['Andrii']}")
        self.assertIn("0991234567", bot.contacts["Andrii"])

    def test_update_old_phone_not_found(self) -> None:
        args = ["Andrii", "0000000000", "0660000000"]
        result = bot.update_phone(args)
        print(f"\n  input:   {args} (old phone not in contact)")
        print(f"  result:  '{result}'")
        self.assertIn("not found", result)

    def test_update_contact_not_found(self) -> None:
        args = ["Petro", "0671234567", "0660000000"]
        result = bot.update_phone(args)
        print(f"\n  input:   {args} (contact does not exist)")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)

    def test_update_invalid_new_phone(self) -> None:
        args = ["Andrii", "0671234567", "abc"]
        result = bot.update_phone(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertIn("ERR", result)
        self.assertIn("0671234567", bot.contacts["Andrii"])

    def test_update_missing_args(self) -> None:
        args = ["Andrii", "0671234567"]
        result = bot.update_phone(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)


# ===========================================================================
# 5. search_contact
# ===========================================================================
class TestSearchContact(BotTestBase):

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567", "0991234567"]

    def test_search_success(self) -> None:
        args = ["Andrii"]
        result = bot.search_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:\n    {result}")
        self.assertIn("Andrii", result)
        self.assertIn("0671234567", result)
        self.assertIn("0991234567", result)

    def test_search_shows_all_phones(self) -> None:
        args = ["Andrii"]
        result = bot.search_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:\n    {result}")
        self.assertIn("1.", result)
        self.assertIn("2.", result)

    def test_search_not_found(self) -> None:
        args = ["Petro"]
        result = bot.search_contact(args)
        print(f"\n  input:   {args} (contact does not exist)")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)

    def test_search_missing_args(self) -> None:
        args = []
        result = bot.search_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)

    def test_search_case_sensitive(self) -> None:
        args = ["andrii"]
        result = bot.search_contact(args)
        print(f"\n  input:   {args} (lowercase, 'Andrii' exists)")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)


# ===========================================================================
# 6. remove_phone
# ===========================================================================
class TestRemovePhone(BotTestBase):

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567", "0991234567"]

    def test_remove_one_phone(self) -> None:
        args = ["Andrii", "0671234567"]
        result = bot.remove_phone(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertIn("removed", result)
        self.assertNotIn("0671234567", bot.contacts["Andrii"])
        self.assertIn("Andrii", bot.contacts)

    def test_remove_last_phone_deletes_contact(self) -> None:
        bot.contacts["Andrii"] = ["0671234567"]
        args = ["Andrii", "0671234567"]
        result = bot.remove_phone(args)
        print(f"\n  input:   {args} (only phone — contact should be deleted)")
        print(f"  result:  '{result}'")
        print(f"  'Andrii' in contacts: {'Andrii' in bot.contacts}")
        self.assertIn("deleted", result)
        self.assertNotIn("Andrii", bot.contacts)

    def test_remove_phone_not_in_contact(self) -> None:
        args = ["Andrii", "0000000000"]
        result = bot.remove_phone(args)
        print(f"\n  input:   {args} (phone not in contact)")
        print(f"  result:  '{result}'")
        print(f"  contacts['Andrii']: {bot.contacts['Andrii']}")
        self.assertIn("not found", result)
        self.assertEqual(len(bot.contacts["Andrii"]), 2)

    def test_remove_contact_not_found(self) -> None:
        args = ["Petro", "0671234567"]
        result = bot.remove_phone(args)
        print(f"\n  input:   {args} (contact does not exist)")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)

    def test_remove_missing_args(self) -> None:
        args = ["Andrii"]
        result = bot.remove_phone(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)


# ===========================================================================
# 7. delete_contact
# ===========================================================================
class TestDeleteContact(BotTestBase):

    def setUp(self) -> None:
        super().setUp()
        bot.contacts["Andrii"] = ["0671234567"]

    def test_delete_success(self) -> None:
        args = ["Andrii"]
        result = bot.delete_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        print(f"  contacts: {dict(bot.contacts)}")
        self.assertIn("deleted", result)
        self.assertNotIn("Andrii", bot.contacts)

    def test_delete_only_target(self) -> None:
        bot.contacts["Maria"] = ["0501234567"]
        args = ["Andrii"]
        bot.delete_contact(args)
        print(f"\n  input:   {args}")
        print(f"  contacts after delete: {dict(bot.contacts)}")
        self.assertIn("Maria", bot.contacts)

    def test_delete_not_found(self) -> None:
        args = ["Petro"]
        result = bot.delete_contact(args)
        print(f"\n  input:   {args} (contact does not exist)")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)

    def test_delete_missing_args(self) -> None:
        args = []
        result = bot.delete_contact(args)
        print(f"\n  input:   {args}")
        print(f"  result:  '{result}'")
        self.assertIn("ERR", result)


# ===========================================================================
# 8. list_contacts
# ===========================================================================
class TestListContacts(BotTestBase):

    def test_list_with_contacts(self) -> None:
        bot.contacts["Andrii"] = ["0671234567"]
        bot.contacts["Maria"]  = ["0501234567"]
        result = bot.list_contacts([])
        print(f"\n  contacts: {dict(bot.contacts)}")
        print(f"  result:\n    {result}")
        self.assertIn("Andrii", result)
        self.assertIn("Maria", result)

    def test_list_shows_multiple_phones(self) -> None:
        bot.contacts["Andrii"] = ["0671234567", "0991234567"]
        result = bot.list_contacts([])
        print(f"\n  contacts: {dict(bot.contacts)}")
        print(f"  result:\n    {result}")
        self.assertIn("0671234567", result)
        self.assertIn("0991234567", result)
        self.assertIn("|", result)

    def test_list_empty(self) -> None:
        result = bot.list_contacts([])
        print(f"\n  contacts: (empty)")
        print(f"  result:  '{result}'")
        self.assertIn("No contacts", result)


# ===========================================================================
# 9. hello / show_help
# ===========================================================================
class TestHelloHelp(BotTestBase):

    def test_hello_returns_string(self) -> None:
        result = bot.hello([])
        print(f"\n  result:  '{result}'")
        self.assertIsInstance(result, str)

    def test_hello_contains_help_hint(self) -> None:
        result = bot.hello([])
        print(f"\n  result:  '{result}'")
        self.assertIn("help", result.lower())

    def test_show_help_returns_help_text(self) -> None:
        result = bot.show_help([])
        print(f"\n  result == HELP_TEXT: {result == bot.HELP_TEXT}")
        self.assertEqual(result, bot.HELP_TEXT)

    def test_help_text_contains_all_commands(self) -> None:
        excluded = {"help"}
        commands = [cmd for cmd in bot.COMMANDS if cmd not in excluded]
        print(f"\n  checking commands: {commands}")
        for cmd in commands:
            print(f"    '{cmd}' in HELP_TEXT: {cmd in bot.HELP_TEXT}")
            self.assertIn(cmd, bot.HELP_TEXT)


# ===========================================================================
# 10. parse_input
# ===========================================================================
class TestParseInput(BotTestBase):

    def test_single_command(self) -> None:
        user_input = "hello"
        cmd, args = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}', args={args}")
        self.assertEqual(cmd, "hello")
        self.assertEqual(args, [])

    def test_command_with_args(self) -> None:
        user_input = "search Andrii"
        cmd, args = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}', args={args}")
        self.assertEqual(cmd, "search")
        self.assertEqual(args, ["Andrii"])

    def test_two_word_command(self) -> None:
        user_input = "create contact Andrii 0671234567"
        cmd, args = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}', args={args}")
        self.assertEqual(cmd, "create contact")
        self.assertEqual(args, ["Andrii", "0671234567"])

    def test_two_word_exit_command(self) -> None:
        user_input = "good bye"
        cmd, args = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}', args={args}")
        self.assertEqual(cmd, "good bye")
        self.assertEqual(args, [])

    def test_case_insensitive_command(self) -> None:
        user_input = "HELLO"
        cmd, _ = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}'")
        self.assertEqual(cmd, "hello")

    def test_mixed_case_command(self) -> None:
        user_input = "Search Andrii"
        cmd, _ = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}'")
        self.assertEqual(cmd, "search")

    def test_preserves_args_case(self) -> None:
        user_input = "search Andrii"
        _, args = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> args={args}")
        self.assertEqual(args[0], "Andrii")

    def test_empty_input(self) -> None:
        user_input = ""
        cmd, args = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}', args={args}")
        self.assertEqual(cmd, "")
        self.assertEqual(args, [])

    def test_whitespace_only(self) -> None:
        user_input = "   "
        cmd, args = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}', args={args}")
        self.assertEqual(cmd, "")
        self.assertEqual(args, [])

    def test_extra_spaces_between_words(self) -> None:
        user_input = "  search   Andrii  "
        cmd, args = bot.parse_input(user_input)
        print(f"\n  input:  '{user_input}' -> cmd='{cmd}', args={args}")
        self.assertEqual(cmd, "search")
        self.assertEqual(args, ["Andrii"])


# ===========================================================================
# Точка входу
# ===========================================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)