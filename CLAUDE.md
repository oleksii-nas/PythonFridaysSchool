# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python school homework repository. Each homework file is a standalone script named `HM<N>_Nasukha.py`.

## Running Scripts

```powershell
# Activate the virtual environment first
.venv\Scripts\python.exe <script.py> [args]

# HM1 requires a folder path argument
.venv\Scripts\python.exe HM1_Nasukha.py <folder_path>

# HM2 runs standalone
.venv\Scripts\python.exe HM2_Nasukha.py
```

## Running Tests

```powershell
.venv\Scripts\python.exe -m pytest          # all tests
.venv\Scripts\python.exe -m pytest test_foo.py::test_bar  # single test
```

No `requirements.txt` or `pyproject.toml` exists — the `.venv` is managed manually.

## Architecture

**HM1_Nasukha.py** — recursive folder sorter:
- `CATEGORY_MAP` maps category names to sets of file extensions
- `TRANSLITERATION` maps Ukrainian Cyrillic characters to Latin equivalents
- `normalize()` transliterates filenames and replaces non-alphanumeric characters with underscores; accepts an `existing_names` set to guarantee uniqueness
- `process_folder()` walks a directory tree recursively, skipping already-sorted category subdirectories, and dispatches each file to `move_file()` or `handle_archive()`
- Archives are extracted into a named subfolder under `archives/`; if extraction fails the raw archive file is moved instead

**HM2_Nasukha.py** — upcoming-birthday finder:
- `get_birthdays_per_week(users)` returns a dict of `{weekday_name: [names]}` for users whose birthday falls within the next 7 days
- Birthdays on Saturday or Sunday are shifted to Monday
- The `users` list at module level serves as the data source