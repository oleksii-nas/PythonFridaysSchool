from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


IMAGE_EXTENSIONS = {"JPEG", "PNG", "JPG", "SVG"}
VIDEO_EXTENSIONS = {"AVI", "MP4", "MOV", "MKV"}
DOCUMENT_EXTENSIONS = {"DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX"}
AUDIO_EXTENSIONS = {"MP3", "OGG", "WAV", "AMR"}
ARCHIVE_EXTENSIONS = {"ZIP", "GZ", "TAR"}

CATEGORY_MAP = {
    "images": IMAGE_EXTENSIONS,
    "video": VIDEO_EXTENSIONS,
    "documents": DOCUMENT_EXTENSIONS,
    "audio": AUDIO_EXTENSIONS,
    "archives": ARCHIVE_EXTENSIONS,
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


def normalize(name: str) -> str:
    transliterated = []
    for char in name:
        lower_char = char.lower()
        if lower_char in TRANSLITERATION:
            converted = TRANSLITERATION[lower_char]
            transliterated.append(converted.capitalize() if char.isupper() else converted)
        else:
            transliterated.append(char)
    normalized_name = "".join(transliterated)
    return re.sub(r"[^A-Za-z0-9]", "_", normalized_name)


def get_category(extension: str) -> str:
    upper_extension = extension.upper()
    for category, extensions in CATEGORY_MAP.items():
        if upper_extension in extensions:
            return category
    return "other"


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

    normalized_stem = normalize(file_path.stem)
    new_name = f"{normalized_stem}{file_path.suffix}"
    target_path = make_unique_path(target_dir, new_name)
    shutil.move(str(file_path), str(target_path))


def handle_archive(file_path: Path, target_root: Path) -> None:
    archives_dir = target_root / "archives"
    archives_dir.mkdir(exist_ok=True)

    normalized_stem = normalize(file_path.stem)
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
            if item.name in {"images", "video", "documents", "audio", "archives", "other"}:
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
    if len(sys.argv) != 2:
        print("Usage: python HM_1.py <folder_path>")
        sys.exit(1)

    root_path = Path(sys.argv[1]).resolve()

    if not root_path.exists() or not root_path.is_dir():
        print(f"Folder not found: {root_path}")
        sys.exit(1)

    process_folder(root_path, root_path)
    print(f"Sorting completed: {root_path}")


if __name__ == "__main__":
    main()
