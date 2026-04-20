from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

OTHER_CATEGORY = "other"

CATEGORY_MAP = {
    "images": {"JPEG", "PNG", "JPG", "SVG"},
    "video": {"AVI", "MP4", "MOV", "MKV"},
    "documents": {"DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX"},
    "audio": {"MP3", "OGG", "WAV", "AMR"},
    "archives": {"ZIP", "GZ", "TAR"},
}

TRANSLITERATION = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "h",
    "ґ": "g",
    "д": "d",
    "е": "e",
    "є": "ie",
    "ж": "zh",
    "з": "z",
    "и": "y",
    "і": "i",
    "ї": "yi",
    "й": "i",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ь": "",
    "ю": "iu",
    "я": "ia",
}


def normalize(name: str, existing_names: set[str] | None = None) -> str:
    transliterated = []
    for char in name:
        lower_char = char.lower()
        if lower_char in TRANSLITERATION:
            converted = TRANSLITERATION[lower_char]
            transliterated.append(converted.capitalize() if char.isupper() else converted)
        else:
            transliterated.append(char)
    normalized_name = "".join(transliterated)
    normalized_name = re.sub(r"[^A-Za-z0-9]", "_", normalized_name)

    if not existing_names:
        return normalized_name

    unique_name = normalized_name
    counter = 1
    while unique_name in existing_names:
        unique_name = f"{normalized_name}_{counter}"
        counter += 1
    return unique_name


def get_category(extension: str) -> str:
    upper_extension = extension.upper()
    for category, extensions in CATEGORY_MAP.items():
        if upper_extension in extensions:
            return category
    return OTHER_CATEGORY


def make_unique_path(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1

    while candidate.exists():
        candidate = directory / f"{stem}_{counter}{suffix}"
        counter += 1
    return candidate


def move_file(file_path: Path, target_root: Path, category: str) -> None:
    target_dir = target_root / category
    target_dir.mkdir(exist_ok=True)

    existing_names = {path.stem for path in target_dir.iterdir()}
    normalized_stem = normalize(file_path.stem, existing_names)
    new_name = f"{normalized_stem}{file_path.suffix}"
    target_path = make_unique_path(target_dir, new_name)
    shutil.move(str(file_path), str(target_path))


def handle_archive(file_path: Path, target_root: Path) -> None:
    archives_dir = target_root / "archives"
    archives_dir.mkdir(exist_ok=True)

    existing_names = {path.name for path in archives_dir.iterdir()}
    normalized_stem = normalize(file_path.stem, existing_names)
    archive_folder = make_unique_path(archives_dir, normalized_stem)
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(file_path), str(archive_folder))
        file_path.unlink()
    except (shutil.ReadError, ValueError):
        fallback_name = f"{normalized_stem}{file_path.suffix}"
        target_path = make_unique_path(archives_dir, fallback_name)
        shutil.move(str(file_path), str(target_path))


def process_folder(folder_path: Path, root_path: Path) -> None:
    for item in folder_path.iterdir():
        if item.is_dir():
            if item.name in {*CATEGORY_MAP.keys(), OTHER_CATEGORY}:
                continue
            process_folder(item, root_path)
            try:
                item.rmdir()
            except OSError:
                pass
            continue

        extension = item.suffix[1:] if item.suffix else ""
        category = get_category(extension)

        if category == "archives":
            handle_archive(item, root_path)
        else:
            move_file(item, root_path, category)


def main() -> None:
    if len(sys.argv) == 2:
        root_path = Path(sys.argv[1]).resolve()
    else:
        print("Usage: python HM_1.py <folder_path>")
        sys.exit(1)

    if not root_path.exists() or not root_path.is_dir():
        print(f"Folder not found: {root_path}")
        sys.exit(1)

    process_folder(root_path, root_path)
    print(f"Sorting completed: {root_path}")


if __name__ == "__main__":
    main()
