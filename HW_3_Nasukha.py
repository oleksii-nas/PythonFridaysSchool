def input_error(func):

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found. Enter existing name."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter user name."
    return inner

contacts = {}


@input_error
def add_contact(args):
    name = args[0]
    phone = args[1]

    contacts[name] = phone
    return f"Contact {name} added."


@input_error
def change_contact(args):
    name = args[0]
    phone = args[1]

    if name not in contacts:
        raise KeyError

    contacts[name] = phone
    return f"Contact {name} updated."


@input_error
def phone_contact(args):
    name = args[0]
    # contacts[name] кине KeyError, якщо такого ключа немає
    return f"{name}: {contacts[name]}"


@input_error
def show_all():
    if not contacts:
        return "No contacts saved yet."
    result = "\n".join(
        f"{name}: {phone}" for name, phone in contacts.items()
    )
    return result

def hello_command():
    return "How can I help you?"

def parse_input(user_input):
    parts = user_input.strip().split()   # ["Add", "Andrii", "0671234567"]

    if not parts:
        return "", []

    cmd = parts[0].lower()
    args = parts[1:]

    return cmd, args

def main():
    print("Welcome to the assistant bot!")
    print("Commands: hello, add, change, phone, show all, exit/close/good bye")

    while True:
        user_input = input("Enter a command: ")

        if not user_input.strip():
            continue

        command, args = parse_input(user_input)

        if command in ("exit", "close") or (command == "good" and args and args[0] == "bye"):
            print("Good bye!")
            break

        elif command == "hello":
            print(hello_command())

        elif command == "add":
            print(add_contact(args))

        elif command == "change":
            print(change_contact(args))

        elif command == "phone":
            print(phone_contact(args))

        elif command == "show" and (args and args[0] == "all"):
            print(show_all())

        else:
            print("Invalid command. Try: hello, add, change, phone, show all, exit")

if __name__ == "__main__":
    main()