# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python school homework repository. Each homework lives in its own
`homework_<N>/` folder containing the script (`HM<N>_Nasukha.py` / `HW_<N>_Nasukha.py`)
and its unit tests (`test_*.py`):

- `homework_1/HM1_Nasukha.py` — recursive folder sorter
- `homework_2/HM2_Nasukha.py` — upcoming-birthday finder
- `homework_3/HW_3_Nasukha.py` — console assistant bot (contacts, global dict)
- `homework_4/HW_4_Nasukha.py` — assistant bot rewritten with OOP (Field/Name/Phone/Record/AddressBook)
- `homework_5/HW_5_Nasukha.py` — adds Birthday field, property-based validation, pagination iterator
- `homework_6/HW_6_Nasukha.py` — adds search and pickle persistence (`address_book.pkl` next to the script, saved on any exit including Ctrl+C)

Homeworks 4–6 deliberately copy and extend the previous one — each folder is
self-contained by design; do not deduplicate across folders.

## Running Scripts

```bash
# macOS / Linux
.venv/bin/python <script.py> [args]

# HM1 requires a folder path argument
.venv/bin/python homework_1/HM1_Nasukha.py <folder_path>

# HM2 runs standalone; HW3–HW6 are interactive REPL bots
.venv/bin/python homework_6/HW_6_Nasukha.py
```

## Running Tests

```bash
.venv/bin/python -m pytest                          # all tests
.venv/bin/python -m pytest homework_1               # one homework
.venv/bin/python -m pytest homework_1/test_hm1_nasukha.py::TestNormalize  # single class
```

Dependencies are listed in `requirements.txt` (pytest only). The root
`conftest.py` renders per-class result tables and writes a timestamped log to
`logs/` after every run (the directory is gitignored).

## Architecture

**HM1_Nasukha.py** — recursive folder sorter:
- `CATEGORY_MAP` maps category names to sets of file extensions
- `TRANSLITERATION` maps Ukrainian Cyrillic characters to Latin equivalents
- `normalize()` transliterates filenames and replaces non-alphanumeric characters with underscores; accepts an `existing_names` set to guarantee uniqueness
- `process_folder()` walks a directory tree recursively (over a snapshot via `list(iterdir())`), skipping already-sorted category subdirectories, and dispatches each file to `move_file()` or `handle_archive()`
- Archives are extracted into a named subfolder under `archives/`; if extraction fails the raw archive file is moved instead and the empty subfolder is removed

**HM2_Nasukha.py** — upcoming-birthday finder:
- `get_birthdays_per_week(users, _today=None)` returns a dict of `{weekday_name: [names]}` for users whose birthday falls within the next 7 days; `_today` exists for deterministic tests
- Birthdays on Saturday or Sunday are shifted to Monday; Feb 29 in a non-leap year is treated as Mar 1
- The `users` list at module level serves as the data source

**HW_3–HW_6** — console assistant bot, one evolution per homework:
- Command dispatch via a `COMMANDS` dict; `parse_input()` recognises two-word commands; `input_error` decorator converts Key/Value/IndexError into user-facing messages
- HW3 stores phones cleaned of `+`, `-` and spaces (`validate_phone` returns the cleaned number)
- HW4+ pass `AddressBook` explicitly into every handler (no globals)
- HW6 persistence: `AddressBook.save()` writes atomically (tmp file + `os.replace`); `AddressBook.load()` returns an empty book for a missing or corrupted file; `main()` saves in a `finally` block so Ctrl+C/EOF do not lose data
