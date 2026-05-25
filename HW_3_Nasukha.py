from typing import Callable


def input_error(func: Callable) -> Callable:
    def inner(*args, **kwargs) -> str | None:
        result: str | None = None
        error:  str | None = None
        try:
            result = func(*args, **kwargs)
        except KeyError as e:
            error = f"ERR: Contact {e} not found. Use 'search <name>' to check existing contacts."
        except ValueError as e:
            error = f"ERR: Invalid data — {e}. Provide both name and phone number."
        except IndexError as e:
            error = f"ERR: Missing arguments — {e}. Type 'help' for usage guide."
        return error if error is not None else result
    return inner

contacts = {}


def validate_phone(phone: str) -> str:
    """Валідація номера — тільки цифри, мінімум 7 символів."""
    cleaned = phone.replace("+", "").replace("-", "").replace(" ", "")
    if not cleaned.isdigit():
        raise ValueError(f"'{phone}' is not a valid phone number. Use digits only.")
    if len(cleaned) < 7:
        raise ValueError(f"'{phone}' is too short. Minimum 7 digits required.")
    return phone


@input_error
def create_contact(args: list[str]) -> str:
    """create contact <name> <phone> — додати новий контакт"""
    name, phone = args[0], args[1]
    validate_phone(phone)
    if name in contacts:
        return f"Contact '{name}' already exists. Use 'add phone {name} <phone>' to add another number."
    contacts[name] = [phone]
    return f"Contact '{name}' created with phone {phone}."


@input_error
def add_phone(args: list[str]) -> str:
    """add phone <name> <phone> — додати ще один номер існуючому контакту"""
    name, phone = args[0], args[1]
    validate_phone(phone)
    if name not in contacts:
        raise KeyError(name)
    if phone in contacts[name]:
        return f"Phone {phone} already exists for '{name}'."
    contacts[name].append(phone)
    return f"Phone {phone} added to '{name}'. Total numbers: {len(contacts[name])}."


@input_error
def update_phone(args: list[str]) -> str:
    """update phone <name> <old_phone> <new_phone> — змінити номер"""
    name, old_phone, new_phone = args[0], args[1], args[2]
    validate_phone(new_phone)
    if name not in contacts:
        raise KeyError(name)
    if old_phone not in contacts[name]:
        return f"Phone {old_phone} not found for '{name}'. Use 'search {name}' to see their numbers."
    contacts[name][contacts[name].index(old_phone)] = new_phone
    return f"Phone updated for '{name}': {old_phone} → {new_phone}."


@input_error
def search_contact(args: list[str]) -> str:
    """search <name> — знайти контакт та всі його номери"""
    name = args[0]
    if name not in contacts:
        raise KeyError(name)
    phones = "\n  ".join(f"{i+1}. {p}" for i, p in enumerate(contacts[name]))
    return f"Contact '{name}':\n  {phones}"


@input_error
def remove_phone(args: list[str]) -> str:
    """remove phone <name> <phone> — видалити конкретний номер"""
    name, phone = args[0], args[1]
    if name not in contacts:
        raise KeyError(name)
    if phone not in contacts[name]:
        return f"Phone {phone} not found for '{name}'."
    contacts[name].remove(phone)
    if not contacts[name]:
        del contacts[name]
        return f"Last phone removed. Contact '{name}' deleted."
    return f"Phone {phone} removed from '{name}'."


@input_error
def delete_contact(args: list[str]) -> str:
    """delete contact <name> — видалити контакт повністю"""
    name = args[0]
    if name not in contacts:
        raise KeyError(name)
    del contacts[name]
    return f"Contact '{name}' deleted."


@input_error
def list_contacts(args: list[str]) -> str:
    """list contacts — показати всі контакти"""
    if not contacts:
        return "No contacts saved yet. Use 'create contact <name> <phone>' to add one."
    lines = []
    for i, (name, phones) in enumerate(contacts.items(), 1):
        phones_str = " | ".join(phones)
        lines.append(f"  {i}. {name}: {phones_str}")
    return "All contacts:\n" + "\n".join(lines)


def hello(args: list[str]) -> str:
    return "Hello! Type 'help' to see all available commands."


HELP_TEXT = """
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
  Tip: names are case-sensitive — "Andrii" ≠ "andrii"
"""


def show_help(args: list[str]) -> str:
    return HELP_TEXT


COMMANDS: dict[str, Callable[[list[str]], str]] = {
    "hello":          hello,
    "help":           show_help,
    "create contact": create_contact,
    "add phone":      add_phone,
    "update phone":   update_phone,
    "remove phone":   remove_phone,
    "delete contact": delete_contact,
    "search":         search_contact,
    "list contacts":  list_contacts,
}

EXIT_COMMANDS = {"exit", "close", "good bye"}
TWO_WORD_KEYS = {k for k in list(COMMANDS) + list(EXIT_COMMANDS) if " " in k}


def parse_input(user_input: str) -> tuple[str, list[str]]:
    parts: list[str] = user_input.strip().split()
    if not parts:
        return "", []
    two_word: str = f"{parts[0].lower()} {parts[1].lower()}" if len(parts) >= 2 else ""
    if two_word in TWO_WORD_KEYS:
        return two_word, parts[2:]
    return parts[0].lower(), parts[1:]


def main() -> None:
    print("Welcome to the Assistant Bot!")
    print("Type 'help' to see all available commands.\n")
    while True:
        user_input: str = input(">>> ")
        if not user_input.strip():
            continue
        command, args = parse_input(user_input)
        if command in EXIT_COMMANDS:
            print("Good bye!")
            break
        match COMMANDS.get(command):
            case None:
                print(f"Unknown command '{command}'. Type 'help' to see available commands.")
            case handler:
                print(handler(args))


if __name__ == "__main__":
    main()