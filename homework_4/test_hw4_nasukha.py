import unittest

from homework_4.HW_4_Nasukha import (
    Field, Name, Phone, Record, AddressBook,
    create_contact, add_phone, update_phone, search_contact,
    remove_phone, delete_contact, list_contacts, hello, show_help,
    parse_input,
)


class TestField(unittest.TestCase):
    def test_str_returns_value(self):
        self.assertEqual(str(Field("test")), "test")

    def test_value_stored(self):
        self.assertEqual(Field("hello").value, "hello")


class TestName(unittest.TestCase):
    def test_valid_name(self):
        self.assertEqual(Name("Alice").value, "Alice")

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            Name("")

    def test_whitespace_name_raises(self):
        with self.assertRaises(ValueError):
            Name("   ")


class TestPhone(unittest.TestCase):
    def test_valid_phone(self):
        self.assertEqual(Phone("1234567890").value, "1234567890")

    def test_too_short_raises(self):
        with self.assertRaises(ValueError):
            Phone("123456789")

    def test_too_long_raises(self):
        with self.assertRaises(ValueError):
            Phone("12345678901")

    def test_non_digits_raises(self):
        with self.assertRaises(ValueError):
            Phone("123456789a")

    def test_with_dashes_raises(self):
        with self.assertRaises(ValueError):
            Phone("123-456-789")

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            Phone("")


class TestRecord(unittest.TestCase):
    def setUp(self):
        self.record = Record("Alice")

    def test_name_stored(self):
        self.assertEqual(self.record.name.value, "Alice")

    def test_phones_empty_on_init(self):
        self.assertEqual(self.record.phones, [])

    def test_add_phone_success(self):
        self.record.add_phone("1234567890")
        self.assertEqual(len(self.record.phones), 1)
        self.assertEqual(self.record.phones[0].value, "1234567890")

    def test_add_phone_duplicate_raises(self):
        self.record.add_phone("1234567890")
        with self.assertRaises(ValueError):
            self.record.add_phone("1234567890")

    def test_add_phone_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.record.add_phone("123")

    def test_add_multiple_phones(self):
        self.record.add_phone("1234567890")
        self.record.add_phone("0987654321")
        self.assertEqual(len(self.record.phones), 2)

    def test_remove_phone_success(self):
        self.record.add_phone("1234567890")
        self.record.remove_phone("1234567890")
        self.assertEqual(self.record.phones, [])

    def test_remove_phone_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.record.remove_phone("1234567890")

    def test_edit_phone_success(self):
        self.record.add_phone("1234567890")
        self.record.edit_phone("1234567890", "0987654321")
        self.assertEqual(self.record.phones[0].value, "0987654321")

    def test_edit_phone_old_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.record.edit_phone("1234567890", "0987654321")

    def test_edit_phone_invalid_new_raises(self):
        self.record.add_phone("1234567890")
        with self.assertRaises(ValueError):
            self.record.edit_phone("1234567890", "123")

    def test_find_phone_found(self):
        self.record.add_phone("1234567890")
        result = self.record.find_phone("1234567890")
        self.assertIsNotNone(result)
        self.assertEqual(result.value, "1234567890")

    def test_find_phone_not_found_returns_none(self):
        self.assertIsNone(self.record.find_phone("1234567890"))

    def test_str_with_phones(self):
        self.record.add_phone("1234567890")
        s = str(self.record)
        self.assertIn("Alice", s)
        self.assertIn("1234567890", s)

    def test_str_no_phones(self):
        self.assertIn("Alice", str(self.record))


class TestAddressBook(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        self.record = Record("Alice")
        self.record.add_phone("1234567890")

    def test_add_record(self):
        self.book.add_record(self.record)
        self.assertIn("Alice", self.book.data)

    def test_find_existing(self):
        self.book.add_record(self.record)
        self.assertIs(self.book.find("Alice"), self.record)

    def test_find_not_existing_returns_none(self):
        self.assertIsNone(self.book.find("Bob"))

    def test_delete_existing(self):
        self.book.add_record(self.record)
        self.book.delete("Alice")
        self.assertNotIn("Alice", self.book.data)

    def test_delete_not_existing_raises(self):
        with self.assertRaises(KeyError):
            self.book.delete("Bob")


class TestCreateContact(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    def test_create_success(self):
        result = create_contact(self.book, ["Alice", "1234567890"])
        self.assertIn("Alice", result)
        self.assertIn("1234567890", result)

    def test_create_stores_in_book(self):
        create_contact(self.book, ["Alice", "1234567890"])
        self.assertIsNotNone(self.book.find("Alice"))

    def test_create_stores_phone_as_phone_object(self):
        create_contact(self.book, ["Alice", "1234567890"])
        record = self.book.find("Alice")
        self.assertEqual(len(record.phones), 1)
        self.assertEqual(record.phones[0].value, "1234567890")

    def test_create_duplicate_returns_message(self):
        create_contact(self.book, ["Alice", "1234567890"])
        result = create_contact(self.book, ["Alice", "0987654321"])
        self.assertIn("already exists", result)

    def test_create_invalid_phone(self):
        result = create_contact(self.book, ["Alice", "123"])
        self.assertIn("ERR", result)

    def test_create_missing_phone(self):
        result = create_contact(self.book, ["Alice"])
        self.assertIn("ERR", result)

    def test_create_missing_all_args(self):
        result = create_contact(self.book, [])
        self.assertIn("ERR", result)


class TestAddPhone(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_add_phone_success(self):
        result = add_phone(self.book, ["Alice", "0987654321"])
        self.assertIn("0987654321", result)

    def test_add_phone_stored_in_record(self):
        add_phone(self.book, ["Alice", "0987654321"])
        self.assertEqual(len(self.book.find("Alice").phones), 2)

    def test_add_phone_contact_not_found(self):
        result = add_phone(self.book, ["Bob", "0987654321"])
        self.assertIn("ERR", result)

    def test_add_phone_duplicate(self):
        result = add_phone(self.book, ["Alice", "1234567890"])
        self.assertIn("ERR", result)

    def test_add_phone_invalid(self):
        result = add_phone(self.book, ["Alice", "123"])
        self.assertIn("ERR", result)

    def test_add_phone_missing_args(self):
        result = add_phone(self.book, ["Alice"])
        self.assertIn("ERR", result)


class TestUpdatePhone(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_update_success(self):
        result = update_phone(self.book, ["Alice", "1234567890", "0987654321"])
        self.assertIn("0987654321", result)

    def test_update_changes_phone_value(self):
        update_phone(self.book, ["Alice", "1234567890", "0987654321"])
        self.assertEqual(self.book.find("Alice").phones[0].value, "0987654321")

    def test_update_keeps_phone_count(self):
        update_phone(self.book, ["Alice", "1234567890", "0987654321"])
        self.assertEqual(len(self.book.find("Alice").phones), 1)

    def test_update_contact_not_found(self):
        result = update_phone(self.book, ["Bob", "1234567890", "0987654321"])
        self.assertIn("ERR", result)

    def test_update_old_phone_not_found(self):
        result = update_phone(self.book, ["Alice", "0000000000", "0987654321"])
        self.assertIn("ERR", result)

    def test_update_invalid_new_phone(self):
        result = update_phone(self.book, ["Alice", "1234567890", "123"])
        self.assertIn("ERR", result)

    def test_update_missing_args(self):
        result = update_phone(self.book, ["Alice", "1234567890"])
        self.assertIn("ERR", result)


class TestSearchContact(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_search_success(self):
        result = search_contact(self.book, ["Alice"])
        self.assertIn("Alice", result)
        self.assertIn("1234567890", result)

    def test_search_shows_all_phones(self):
        add_phone(self.book, ["Alice", "0987654321"])
        result = search_contact(self.book, ["Alice"])
        self.assertIn("1234567890", result)
        self.assertIn("0987654321", result)

    def test_search_not_found(self):
        result = search_contact(self.book, ["Bob"])
        self.assertIn("ERR", result)

    def test_search_case_sensitive(self):
        result = search_contact(self.book, ["alice"])
        self.assertIn("ERR", result)

    def test_search_missing_args(self):
        result = search_contact(self.book, [])
        self.assertIn("ERR", result)

    def test_search_contact_no_phones(self):
        record = Record("NoPhone")
        self.book.add_record(record)
        result = search_contact(self.book, ["NoPhone"])
        self.assertIn("no phones", result)


class TestRemovePhone(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_remove_one_phone(self):
        add_phone(self.book, ["Alice", "0987654321"])
        result = remove_phone(self.book, ["Alice", "1234567890"])
        self.assertIn("removed", result)
        self.assertEqual(len(self.book.find("Alice").phones), 1)

    def test_remove_last_phone_deletes_contact(self):
        result = remove_phone(self.book, ["Alice", "1234567890"])
        self.assertIn("deleted", result)
        self.assertIsNone(self.book.find("Alice"))

    def test_remove_contact_not_found(self):
        result = remove_phone(self.book, ["Bob", "1234567890"])
        self.assertIn("ERR", result)

    def test_remove_phone_not_in_contact(self):
        result = remove_phone(self.book, ["Alice", "0000000000"])
        self.assertIn("ERR", result)

    def test_remove_missing_args(self):
        result = remove_phone(self.book, ["Alice"])
        self.assertIn("ERR", result)


class TestDeleteContact(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_delete_success(self):
        result = delete_contact(self.book, ["Alice"])
        self.assertIn("deleted", result)

    def test_delete_removes_from_book(self):
        delete_contact(self.book, ["Alice"])
        self.assertIsNone(self.book.find("Alice"))

    def test_delete_not_found(self):
        result = delete_contact(self.book, ["Bob"])
        self.assertIn("ERR", result)

    def test_delete_missing_args(self):
        result = delete_contact(self.book, [])
        self.assertIn("ERR", result)

    def test_delete_only_target(self):
        create_contact(self.book, ["Bob", "0987654321"])
        delete_contact(self.book, ["Alice"])
        self.assertIsNotNone(self.book.find("Bob"))


class TestListContacts(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    def test_list_empty(self):
        result = list_contacts(self.book, [])
        self.assertIn("No contacts", result)

    def test_list_with_contacts(self):
        create_contact(self.book, ["Alice", "1234567890"])
        result = list_contacts(self.book, [])
        self.assertIn("Alice", result)
        self.assertIn("1234567890", result)

    def test_list_shows_multiple_phones(self):
        create_contact(self.book, ["Alice", "1234567890"])
        add_phone(self.book, ["Alice", "0987654321"])
        result = list_contacts(self.book, [])
        self.assertIn("1234567890", result)
        self.assertIn("0987654321", result)

    def test_list_multiple_contacts(self):
        create_contact(self.book, ["Alice", "1234567890"])
        create_contact(self.book, ["Bob", "0987654321"])
        result = list_contacts(self.book, [])
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)


class TestHelloHelp(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    def test_hello_returns_string(self):
        self.assertIsInstance(hello(self.book, []), str)

    def test_hello_contains_help_hint(self):
        self.assertIn("help", hello(self.book, []).lower())

    def test_show_help_returns_string(self):
        self.assertIsInstance(show_help(self.book, []), str)

    def test_help_text_contains_all_commands(self):
        result = show_help(self.book, [])
        for cmd in ["create contact", "add phone", "update phone",
                    "remove phone", "delete contact", "search", "list contacts"]:
            self.assertIn(cmd, result)


class TestParseInput(unittest.TestCase):
    def test_empty_input(self):
        cmd, args = parse_input("")
        self.assertEqual(cmd, "")
        self.assertEqual(args, [])

    def test_whitespace_only(self):
        cmd, args = parse_input("   ")
        self.assertEqual(cmd, "")
        self.assertEqual(args, [])

    def test_single_command(self):
        cmd, args = parse_input("hello")
        self.assertEqual(cmd, "hello")
        self.assertEqual(args, [])

    def test_command_with_args(self):
        cmd, args = parse_input("search Alice")
        self.assertEqual(cmd, "search")
        self.assertEqual(args, ["Alice"])

    def test_two_word_command(self):
        cmd, args = parse_input("create contact Alice 1234567890")
        self.assertEqual(cmd, "create contact")
        self.assertEqual(args, ["Alice", "1234567890"])

    def test_case_insensitive_command(self):
        cmd, _ = parse_input("HELLO")
        self.assertEqual(cmd, "hello")

    def test_mixed_case_two_word_command(self):
        cmd, args = parse_input("Add Phone Alice 1234567890")
        self.assertEqual(cmd, "add phone")
        self.assertEqual(args, ["Alice", "1234567890"])

    def test_preserves_args_case(self):
        _, args = parse_input("search Alice")
        self.assertEqual(args[0], "Alice")

    def test_two_word_exit_command(self):
        cmd, _ = parse_input("good bye")
        self.assertEqual(cmd, "good bye")

    def test_extra_spaces_trimmed(self):
        cmd, _ = parse_input("  hello  ")
        self.assertEqual(cmd, "hello")


if __name__ == "__main__":
    unittest.main()
