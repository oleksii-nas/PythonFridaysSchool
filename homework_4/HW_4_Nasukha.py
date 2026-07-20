from __future__ import annotations

from collections import UserDict
from typing import Callable, Dict, List, Set, Tuple


# ===========================================================================
# ДЕКОРАТОР — стиль ДЗ 3
# ===========================================================================
def input_error(func: Callable[..., str]) -> Callable[..., str | None]:
    def inner(*args, **kwargs) -> str | None:
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return f"ERR: Contact {e} not found."
        except ValueError as e:
            return f"ERR: Invalid data — {e}."
        except IndexError as e:
            return f"ERR: Missing arguments — {e}. Type 'help' for usage guide."

    return inner


# ===========================================================================
# БЛОК МОДЕЛЕЙ (OOP)
# ===========================================================================
class Field:
    """Базовий клас для всіх полів запису."""

    def __init__(self, value: str) -> None:
        self.value: str = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Обов'язкове поле — ім'я контакту."""

    def __init__(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    """
    Необов'язкове поле — номер телефону.
    Валідація: рівно 10 цифр.
    """

    def __init__(self, value: str) -> None:
        Phone._validate(value)
        super().__init__(value)

    @staticmethod
    def _validate(phone: str) -> None:
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError(
                f"'{phone}' is not valid. Phone must contain exactly 10 digits."
            )


class Record:
    """
    Запис контакту: ім'я + список телефонів.
    Відповідає за додавання / видалення / редагування полів.
    """

    name: Name
    phones: List[Phone]

    def __init__(self, name: str) -> None:
        self.name: Name = Name(name)
        self.phones: List[Phone] = []

    def add_phone(self, phone: str) -> None:
        """Додати новий номер телефону."""
        if self.find_phone(phone):
            raise ValueError(f"Phone {phone} already exists for '{self.name.value}'.")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        """Видалити номер телефону."""
        found: Phone | None = self.find_phone(phone)
        if found is None:
            raise ValueError(f"Phone {phone} not found for '{self.name.value}'.")
        self.phones.remove(found)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Замінити існуючий номер на новий."""
        found: Phone | None = self.find_phone(old_phone)
        if found is None:
            raise ValueError(f"Phone {old_phone} not found for '{self.name.value}'.")
        found.value = Phone(new_phone).value

    def find_phone(self, phone: str) -> Phone | None:
        """Знайти об'єкт Phone за значенням. Повертає Phone або None."""
        return next((p for p in self.phones if p.value == phone), None)

    def __str__(self) -> str:
        phones_str: str = "; ".join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}"


class AddressBook(UserDict[str, Record]):
    """
    Адресна книга — успадковується від UserDict.
    Ключ: ім'я контакту (str), Значення: об'єкт Record.
    """

    def add_record(self, record: Record) -> None:
        """Додати запис до книги."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        """Знайти запис за іменем. Повертає Record або None."""
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Видалити запис за іменем."""
        if name not in self.data:
            raise KeyError(f"'{name}'")
        del self.data[name]


# ===========================================================================
# ХЕНДЛЕРИ — стиль ДЗ 3
# ===========================================================================
@input_error
def create_contact(book: AddressBook, args: List[str]) -> str:
    """create contact <name> <phone>"""
    name, phone = args[0], args[1]
    if book.find(name):
        return f"Contact '{name}' already exists. Use 'add phone {name} <phone>' to add a number."
    record: Record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return f"Contact '{name}' created with phone {phone}."


@input_error
def add_phone(book: AddressBook, args: List[str]) -> str:
    """add phone <name> <phone>"""
    name, phone = args[0], args[1]
    record: Record | None = book.find(name)
    if record is None:
        raise KeyError(f"'{name}'")
    record.add_phone(phone)
    return f"Phone {phone} added to '{name}'. Total: {len(record.phones)}."


@input_error
def update_phone(book: AddressBook, args: List[str]) -> str:
    """update phone <name> <old_phone> <new_phone>"""
    name, old_phone, new_phone = args[0], args[1], args[2]
    record: Record | None = book.find(name)
    if record is None:
        raise KeyError(f"'{name}'")
    record.edit_phone(old_phone, new_phone)
    return f"Phone updated for '{name}': {old_phone} → {new_phone}."


@input_error
def search_contact(book: AddressBook, args: List[str]) -> str:
    """search <name>"""
    name: str = args[0]
    record: Record | None = book.find(name)
    if record is None:
        raise KeyError(f"'{name}'")
    phones: str = "\n  ".join(
        f"{i + 1}. {p.value}" for i, p in enumerate(record.phones)
    )
    return (
        f"Contact '{name}':\n  {phones}"
        if phones
        else f"Contact '{name}' has no phones."
    )


@input_error
def remove_phone(book: AddressBook, args: List[str]) -> str:
    """remove phone <name> <phone>"""
    name, phone = args[0], args[1]
    record: Record | None = book.find(name)
    if record is None:
        raise KeyError(f"'{name}'")
    record.remove_phone(phone)
    if not record.phones:
        book.delete(name)
        return f"Last phone removed. Contact '{name}' deleted."
    return f"Phone {phone} removed from '{name}'."


@input_error
def delete_contact(book: AddressBook, args: List[str]) -> str:
    """delete contact <name>"""
    name: str = args[0]
    book.delete(name)
    return f"Contact '{name}' deleted."


@input_error
def list_contacts(book: AddressBook, args: List[str]) -> str:
    """list contacts"""
    if not book.data:
        return "No contacts saved yet. Use 'create contact <name> <phone>' to add one."
    lines: List[str] = [f"  {i}. {record}" for i, record in enumerate(book.values(), 1)]
    return "All contacts:\n" + "\n".join(lines)


def hello(book: AddressBook, args: List[str]) -> str:
    return "Hello! Type 'help' to see all available commands."


# ===========================================================================
# ДОВІДКА
# ===========================================================================
HELP_TEXT: str = """
╔══════════════════════════════════════════════════════════════╗
║                     AVAILABLE COMMANDS                       ║
╠══════════════════════════════════════════════════════════════╣
║  hello                                — greeting             ║
║  create contact <name> <phone>        — add new contact      ║
║  add phone <name> <phone>             — add extra phone      ║
║  update phone <name> <old> <new>      — change phone number  ║
║  remove phone <name> <phone>          — delete one phone     ║
║  delete contact <name>                — delete contact       ║
║  search <name>                        — find contact         ║
║  list contacts                        — show all contacts    ║
╠══════════════════════════════════════════════════════════════╣
║  exit  |  close  |  good bye          — quit the program     ║
╚══════════════════════════════════════════════════════════════╝
  Tip: phone must be exactly 10 digits  |  names are case-sensitive
"""


def show_help(book: AddressBook, args: List[str]) -> str:
    return HELP_TEXT


# ===========================================================================
# ТАБЛИЦЯ КОМАНД — стиль ДЗ 3
# ===========================================================================
COMMANDS: Dict[str, Callable[[AddressBook, List[str]], str | None]] = {
    "hello": hello,
    "help": show_help,
    "create contact": create_contact,
    "add phone": add_phone,
    "update phone": update_phone,
    "remove phone": remove_phone,
    "delete contact": delete_contact,
    "search": search_contact,
    "list contacts": list_contacts,
}

EXIT_COMMANDS: Set[str] = {"exit", "close", "good bye"}
TWO_WORD_KEYS: Set[str] = {k for k in list(COMMANDS) + list(EXIT_COMMANDS) if " " in k}


# ===========================================================================
# ПАРСЕР — стиль ДЗ 3
# ===========================================================================
def parse_input(user_input: str) -> Tuple[str, List[str]]:
    parts: List[str] = user_input.strip().split()
    if not parts:
        return "", []
    two_word: str = f"{parts[0].lower()} {parts[1].lower()}" if len(parts) >= 2 else ""
    if two_word in TWO_WORD_KEYS:
        return two_word, parts[2:]
    return parts[0].lower(), parts[1:]


# ===========================================================================
# ГОЛОВНИЙ ЦИКЛ — стиль ДЗ 3
# ===========================================================================
def main() -> None:
    print("Welcome to the Assistant Bot!")
    print("Type 'help' to see all available commands.\n")

    book: AddressBook = AddressBook()

    while True:
        user_input: str = input(">>> ")
        if not user_input.strip():
            continue
        command, args = parse_input(user_input)
        if command in EXIT_COMMANDS:
            print("Good bye!")
            break
        handler: Callable[[AddressBook, List[str]], str | None] | None = (
            COMMANDS.get(command)
        )
        if handler is None:
            print(
                f"Unknown command '{command}'. Type 'help' to see available commands."
            )
        else:
            print(handler(book, args))


if __name__ == "__main__":
    main()
