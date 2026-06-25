import pickle
import tempfile
import unittest
from datetime import date
from pathlib import Path

from homework_6.HW_6_Nasukha import (
    Field, Name, Phone, Birthday, Record, AddressBook,
    create_contact, add_phone, update_phone, search_contact,
    find_contacts, remove_phone, delete_contact, list_contacts,
    add_birthday, birthday_cmd,
    hello, show_help, parse_input,
)


# ===========================================================================
# Field
# ===========================================================================
class TestField(unittest.TestCase):
    def test_str_returns_value(self):
        self.assertEqual(str(Field("test")), "test")

    def test_value_getter(self):
        self.assertEqual(Field("hello").value, "hello")

    def test_value_setter(self):
        f = Field("a")
        f.value = "b"
        self.assertEqual(f.value, "b")


# ===========================================================================
# Name
# ===========================================================================
class TestName(unittest.TestCase):
    def test_valid_name(self):
        self.assertEqual(Name("Alice").value, "Alice")

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            Name("")

    def test_whitespace_name_raises(self):
        with self.assertRaises(ValueError):
            Name("   ")


# ===========================================================================
# Phone
# ===========================================================================
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

    def test_setter_validates_on_reassign(self):
        p = Phone("1234567890")
        with self.assertRaises(ValueError):
            p.value = "123"

    def test_setter_accepts_valid_reassign(self):
        p = Phone("1234567890")
        p.value = "0987654321"
        self.assertEqual(p.value, "0987654321")


# ===========================================================================
# Birthday
# ===========================================================================
class TestBirthday(unittest.TestCase):
    def test_valid_birthday(self):
        b = Birthday("01.01.1990")
        self.assertIsInstance(b.value, date)
        self.assertEqual(b.value, date(1990, 1, 1))

    def test_str_format(self):
        self.assertEqual(str(Birthday("25.12.2000")), "25.12.2000")

    def test_invalid_format_dashes_raises(self):
        with self.assertRaises(ValueError):
            Birthday("01-01-1990")

    def test_invalid_format_iso_raises(self):
        with self.assertRaises(ValueError):
            Birthday("1990.01.01")

    def test_invalid_month_raises(self):
        with self.assertRaises(ValueError):
            Birthday("01.13.2000")

    def test_invalid_day_raises(self):
        with self.assertRaises(ValueError):
            Birthday("32.01.2000")

    def test_feb29_nonleap_raises(self):
        with self.assertRaises(ValueError):
            Birthday("29.02.2001")

    def test_feb29_leap_valid(self):
        b = Birthday("29.02.2000")
        self.assertEqual(b.value, date(2000, 2, 29))

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            Birthday("")

    def test_setter_validates_on_reassign(self):
        b = Birthday("01.01.1990")
        with self.assertRaises(ValueError):
            b.value = "bad-date"

    def test_setter_accepts_valid_reassign(self):
        b = Birthday("01.01.1990")
        b.value = "15.06.1985"
        self.assertEqual(b.value, date(1985, 6, 15))


# ===========================================================================
# Record — основний функціонал
# ===========================================================================
class TestRecord(unittest.TestCase):
    def setUp(self):
        self.record = Record("Alice")

    def test_name_stored(self):
        self.assertEqual(self.record.name.value, "Alice")

    def test_phones_empty_on_init(self):
        self.assertEqual(self.record.phones, [])

    def test_birthday_none_on_init(self):
        self.assertIsNone(self.record.birthday)

    def test_birthday_set_via_init(self):
        r = Record("Bob", "10.05.1990")
        self.assertIsNotNone(r.birthday)
        self.assertEqual(str(r.birthday), "10.05.1990")

    def test_add_phone_success(self):
        self.record.add_phone("1234567890")
        self.assertEqual(len(self.record.phones), 1)

    def test_add_phone_duplicate_raises(self):
        self.record.add_phone("1234567890")
        with self.assertRaises(ValueError):
            self.record.add_phone("1234567890")

    def test_add_phone_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.record.add_phone("123")

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

    def test_str_with_birthday(self):
        self.record.add_birthday("01.01.1990")
        self.assertIn("01.01.1990", str(self.record))

    def test_str_no_birthday_not_shown(self):
        self.assertNotIn("birthday", str(self.record))


# ===========================================================================
# Record — день народження
# ===========================================================================
class TestRecordBirthday(unittest.TestCase):
    def setUp(self):
        self.record = Record("Alice")

    def test_add_birthday_stores(self):
        self.record.add_birthday("15.06.1990")
        self.assertEqual(str(self.record.birthday), "15.06.1990")

    def test_add_birthday_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.record.add_birthday("not-a-date")

    def test_add_birthday_overwrites(self):
        self.record.add_birthday("15.06.1990")
        self.record.add_birthday("20.07.1985")
        self.assertEqual(str(self.record.birthday), "20.07.1985")

    def test_days_to_birthday_no_birthday_returns_none(self):
        self.assertIsNone(self.record.days_to_birthday())

    def test_days_to_birthday_today_returns_zero(self):
        self.record.add_birthday("24.06.1990")
        self.assertEqual(self.record.days_to_birthday(_today=date(2026, 6, 24)), 0)

    def test_days_to_birthday_tomorrow_returns_one(self):
        self.record.add_birthday("25.06.1990")
        self.assertEqual(self.record.days_to_birthday(_today=date(2026, 6, 24)), 1)

    def test_days_to_birthday_already_passed_uses_next_year(self):
        today = date(2026, 6, 24)
        self.record.add_birthday("01.06.1990")
        days = self.record.days_to_birthday(_today=today)
        self.assertEqual(days, (date(2027, 6, 1) - today).days)

    def test_days_to_birthday_feb29_uses_mar1(self):
        today = date(2026, 2, 27)
        self.record.add_birthday("29.02.2000")
        self.assertEqual(self.record.days_to_birthday(_today=today), 2)


# ===========================================================================
# AddressBook — базові операції
# ===========================================================================
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


# ===========================================================================
# AddressBook — пагінація
# ===========================================================================
class TestAddressBookIterator(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        for i, name in enumerate(["Alice", "Bob", "Charlie", "Dave", "Eve"]):
            r = Record(name)
            r.add_phone(f"123456789{i}")
            self.book.add_record(r)

    def test_empty_book_no_batches(self):
        batches = list(AddressBook().iterator(2))
        self.assertEqual(batches, [])

    def test_batch_count(self):
        self.assertEqual(len(list(self.book.iterator(2))), 3)

    def test_batch_sizes(self):
        batches = list(self.book.iterator(2))
        self.assertEqual([len(b) for b in batches], [2, 2, 1])

    def test_n_equals_total(self):
        batches = list(self.book.iterator(5))
        self.assertEqual(len(batches), 1)
        self.assertEqual(len(batches[0]), 5)

    def test_n_greater_than_total(self):
        batches = list(self.book.iterator(10))
        self.assertEqual(len(batches), 1)

    def test_n_equals_one(self):
        batches = list(self.book.iterator(1))
        self.assertEqual(len(batches), 5)

    def test_all_records_included(self):
        names = {r.name.value for batch in self.book.iterator(2) for r in batch}
        self.assertEqual(names, {"Alice", "Bob", "Charlie", "Dave", "Eve"})

    def test_returns_generator(self):
        import types
        self.assertIsInstance(self.book.iterator(2), types.GeneratorType)


# ===========================================================================
# AddressBook — пошук (search)
# ===========================================================================
class TestAddressBookSearch(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        alice = Record("Alice")
        alice.add_phone("1234567890")
        alice.add_phone("1111111111")
        self.book.add_record(alice)

        bob = Record("Bob")
        bob.add_phone("0987654321")
        self.book.add_record(bob)

        charlie = Record("Charlie")
        charlie.add_phone("1230000000")
        self.book.add_record(charlie)

    def test_search_by_full_name(self):
        results = self.book.search("Alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name.value, "Alice")

    def test_search_by_partial_name(self):
        results = self.book.search("ali")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name.value, "Alice")

    def test_search_by_name_case_insensitive(self):
        results = self.book.search("ALICE")
        self.assertEqual(len(results), 1)

    def test_search_by_partial_phone(self):
        # "123" є в Alice (1234567890, 1111111111? ні), Charlie (1230000000)
        results = self.book.search("123")
        names = {r.name.value for r in results}
        self.assertIn("Alice", names)
        self.assertIn("Charlie", names)
        self.assertNotIn("Bob", names)

    def test_search_by_full_phone(self):
        results = self.book.search("0987654321")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name.value, "Bob")

    def test_search_no_match_returns_empty(self):
        results = self.book.search("zzz")
        self.assertEqual(results, [])

    def test_search_matches_multiple_contacts(self):
        # "1" є в Alice і Charlie
        results = self.book.search("1")
        self.assertGreaterEqual(len(results), 2)

    def test_search_empty_query_matches_all(self):
        # порожній рядок є підрядком будь-якого рядка
        results = self.book.search("")
        self.assertEqual(len(results), 3)

    def test_search_returns_list_of_records(self):
        results = self.book.search("Alice")
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], Record)


# ===========================================================================
# AddressBook — збереження та завантаження
# ===========================================================================
class TestAddressBookPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".pkl", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        Path(self.path).unlink(missing_ok=True)

    def _make_book(self) -> AddressBook:
        book = AddressBook()
        r1 = Record("Alice")
        r1.add_phone("1234567890")
        r1.add_birthday("01.01.1990")
        book.add_record(r1)
        r2 = Record("Bob")
        r2.add_phone("0987654321")
        book.add_record(r2)
        return book

    def test_save_creates_file(self):
        book = self._make_book()
        book.save(self.path)
        self.assertTrue(Path(self.path).exists())

    def test_load_restores_contacts(self):
        self._make_book().save(self.path)
        loaded = AddressBook.load(self.path)
        self.assertIn("Alice", loaded.data)
        self.assertIn("Bob", loaded.data)

    def test_load_restores_phones(self):
        self._make_book().save(self.path)
        loaded = AddressBook.load(self.path)
        alice = loaded.find("Alice")
        self.assertEqual(alice.phones[0].value, "1234567890")

    def test_load_restores_birthday(self):
        self._make_book().save(self.path)
        loaded = AddressBook.load(self.path)
        alice = loaded.find("Alice")
        self.assertIsNotNone(alice.birthday)
        self.assertEqual(str(alice.birthday), "01.01.1990")

    def test_load_nonexistent_file_returns_empty_book(self):
        loaded = AddressBook.load("/tmp/nonexistent_hw6_test.pkl")
        self.assertEqual(len(loaded.data), 0)

    def test_save_and_load_roundtrip_preserves_all_data(self):
        original = self._make_book()
        original.save(self.path)
        loaded = AddressBook.load(self.path)
        self.assertEqual(len(original.data), len(loaded.data))
        for name in original.data:
            orig_rec = original.find(name)
            load_rec = loaded.find(name)
            self.assertEqual(
                [p.value for p in orig_rec.phones],
                [p.value for p in load_rec.phones],
            )

    def test_overwrite_save(self):
        book1 = AddressBook()
        r = Record("Alice")
        r.add_phone("1234567890")
        book1.add_record(r)
        book1.save(self.path)

        book2 = AddressBook()
        r2 = Record("Bob")
        r2.add_phone("0987654321")
        book2.add_record(r2)
        book2.save(self.path)

        loaded = AddressBook.load(self.path)
        self.assertNotIn("Alice", loaded.data)
        self.assertIn("Bob", loaded.data)

    def test_empty_book_save_and_load(self):
        AddressBook().save(self.path)
        loaded = AddressBook.load(self.path)
        self.assertEqual(len(loaded.data), 0)


# ===========================================================================
# Хендлери — create_contact, add_phone, update_phone
# ===========================================================================
class TestCreateContact(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    def test_create_success(self):
        result = create_contact(self.book, ["Alice", "1234567890"])
        self.assertIn("Alice", result)

    def test_create_stores_in_book(self):
        create_contact(self.book, ["Alice", "1234567890"])
        self.assertIsNotNone(self.book.find("Alice"))

    def test_create_duplicate_returns_message(self):
        create_contact(self.book, ["Alice", "1234567890"])
        result = create_contact(self.book, ["Alice", "0987654321"])
        self.assertIn("already exists", result)

    def test_create_invalid_phone(self):
        result = create_contact(self.book, ["Alice", "123"])
        self.assertIn("ERR", result)

    def test_create_missing_args(self):
        result = create_contact(self.book, [])
        self.assertIn("ERR", result)


class TestAddPhone(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_add_phone_success(self):
        result = add_phone(self.book, ["Alice", "0987654321"])
        self.assertIn("0987654321", result)

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

    def test_update_changes_value(self):
        update_phone(self.book, ["Alice", "1234567890", "0987654321"])
        self.assertEqual(self.book.find("Alice").phones[0].value, "0987654321")

    def test_update_contact_not_found(self):
        result = update_phone(self.book, ["Bob", "1234567890", "0987654321"])
        self.assertIn("ERR", result)

    def test_update_invalid_new_phone(self):
        result = update_phone(self.book, ["Alice", "1234567890", "123"])
        self.assertIn("ERR", result)

    def test_update_missing_args(self):
        result = update_phone(self.book, ["Alice", "1234567890"])
        self.assertIn("ERR", result)


# ===========================================================================
# Хендлери — search_contact, find_contacts
# ===========================================================================
class TestSearchContact(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_search_success(self):
        result = search_contact(self.book, ["Alice"])
        self.assertIn("1234567890", result)

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
        self.book.add_record(Record("NoPhone"))
        result = search_contact(self.book, ["NoPhone"])
        self.assertIn("no phones", result)


class TestFindContacts(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])
        create_contact(self.book, ["Bob", "0987654321"])
        create_contact(self.book, ["Charlie", "1230000000"])

    def test_find_by_partial_name(self):
        result = find_contacts(self.book, ["ali"])
        self.assertIn("Alice", result)

    def test_find_case_insensitive(self):
        result = find_contacts(self.book, ["ALICE"])
        self.assertIn("Alice", result)

    def test_find_by_partial_phone(self):
        result = find_contacts(self.book, ["123"])
        self.assertIn("Alice", result)
        self.assertIn("Charlie", result)

    def test_find_no_match(self):
        result = find_contacts(self.book, ["zzz"])
        self.assertIn("No contacts found", result)

    def test_find_multiple_results(self):
        result = find_contacts(self.book, ["1"])
        self.assertIn("Found", result)

    def test_find_missing_args(self):
        result = find_contacts(self.book, [])
        self.assertIn("ERR", result)

    def test_find_shows_count(self):
        result = find_contacts(self.book, ["Alice"])
        self.assertIn("1", result)


# ===========================================================================
# Хендлери — remove, delete, list, birthday
# ===========================================================================
class TestRemovePhone(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_remove_one_phone(self):
        add_phone(self.book, ["Alice", "0987654321"])
        remove_phone(self.book, ["Alice", "1234567890"])
        self.assertEqual(len(self.book.find("Alice").phones), 1)

    def test_remove_last_phone_deletes_contact(self):
        result = remove_phone(self.book, ["Alice", "1234567890"])
        self.assertIn("deleted", result)
        self.assertIsNone(self.book.find("Alice"))

    def test_remove_contact_not_found(self):
        result = remove_phone(self.book, ["Bob", "1234567890"])
        self.assertIn("ERR", result)


class TestDeleteContact(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_delete_success(self):
        delete_contact(self.book, ["Alice"])
        self.assertIsNone(self.book.find("Alice"))

    def test_delete_not_found(self):
        result = delete_contact(self.book, ["Bob"])
        self.assertIn("ERR", result)


class TestListContacts(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    def test_list_empty(self):
        self.assertIn("No contacts", list_contacts(self.book, []))

    def test_list_with_contacts(self):
        create_contact(self.book, ["Alice", "1234567890"])
        result = list_contacts(self.book, [])
        self.assertIn("Alice", result)

    def test_list_shows_birthday(self):
        create_contact(self.book, ["Alice", "1234567890"])
        add_birthday(self.book, ["Alice", "01.01.1990"])
        self.assertIn("01.01.1990", list_contacts(self.book, []))


class TestAddBirthday(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_add_birthday_success(self):
        result = add_birthday(self.book, ["Alice", "01.01.1990"])
        self.assertIn("01.01.1990", result)

    def test_add_birthday_contact_not_found(self):
        result = add_birthday(self.book, ["Bob", "01.01.1990"])
        self.assertIn("ERR", result)

    def test_add_birthday_invalid_format(self):
        result = add_birthday(self.book, ["Alice", "1990-01-01"])
        self.assertIn("ERR", result)

    def test_add_birthday_missing_args(self):
        result = add_birthday(self.book, ["Alice"])
        self.assertIn("ERR", result)


class TestBirthdayCmd(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        create_contact(self.book, ["Alice", "1234567890"])

    def test_no_birthday_set(self):
        result = birthday_cmd(self.book, ["Alice"])
        self.assertIn("no birthday", result)

    def test_contact_not_found(self):
        result = birthday_cmd(self.book, ["Bob"])
        self.assertIn("ERR", result)

    def test_returns_days_string(self):
        add_birthday(self.book, ["Alice", "01.01.1990"])
        result = birthday_cmd(self.book, ["Alice"])
        self.assertIsInstance(result, str)
        self.assertIn("Alice", result)


# ===========================================================================
# hello / show_help
# ===========================================================================
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
        for cmd in [
            "create contact", "add phone", "update phone",
            "remove phone", "delete contact", "search", "find",
            "list contacts", "add birthday", "birthday",
        ]:
            self.assertIn(cmd, result)


# ===========================================================================
# parse_input
# ===========================================================================
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

    def test_find_command(self):
        cmd, args = parse_input("find ali")
        self.assertEqual(cmd, "find")
        self.assertEqual(args, ["ali"])

    def test_two_word_command(self):
        cmd, args = parse_input("create contact Alice 1234567890")
        self.assertEqual(cmd, "create contact")
        self.assertEqual(args, ["Alice", "1234567890"])

    def test_add_birthday_command(self):
        cmd, args = parse_input("add birthday Alice 01.01.1990")
        self.assertEqual(cmd, "add birthday")
        self.assertEqual(args, ["Alice", "01.01.1990"])

    def test_case_insensitive_command(self):
        cmd, _ = parse_input("HELLO")
        self.assertEqual(cmd, "hello")

    def test_mixed_case_two_word_command(self):
        cmd, _ = parse_input("Add Phone Alice 1234567890")
        self.assertEqual(cmd, "add phone")

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
