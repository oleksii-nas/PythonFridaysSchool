"""
Unit тести для HM1_Nasukha.py — рекурсивний сортувальник файлів.

Структура:
  TestNormalize      — транслітерація та нормалізація імен
  TestGetCategory    — визначення категорії за розширенням
  TestMakeUniquePath — генерація унікальних шляхів
  TestMoveFile       — переміщення файлів у категорії
  TestHandleArchive  — розпакування / fallback для архівів
  TestProcessFolder  — рекурсивний обхід дерева

Запуск:
  python -m pytest homework_1 -v
"""

from __future__ import annotations

import importlib
import os
import shutil
import sys
import unittest
import zipfile
from pathlib import Path
from tempfile import mkdtemp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sorter = importlib.import_module("HM1_Nasukha")


class SorterTestBase(unittest.TestCase):
    """Створює тимчасову теку перед кожним тестом і прибирає її після."""

    def setUp(self) -> None:
        self.tmp = Path(mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def touch(self, name: str, root: Path | None = None) -> Path:
        target = (root or self.tmp) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("data", encoding="utf-8")
        return target


# ===========================================================================
# 1. normalize
# ===========================================================================
class TestNormalize(SorterTestBase):
    def test_transliterates_cyrillic(self) -> None:
        self.assertEqual(sorter.normalize("привіт"), "pryvit")

    def test_keeps_uppercase_first_letter(self) -> None:
        self.assertEqual(sorter.normalize("Жук"), "Zhuk")

    def test_replaces_non_alnum_with_underscore(self) -> None:
        self.assertEqual(sorter.normalize("my file (1)!"), "my_file__1__")

    def test_keeps_latin_and_digits(self) -> None:
        self.assertEqual(sorter.normalize("File123"), "File123")

    def test_unique_name_appends_counter(self) -> None:
        existing = {"file", "file_1"}
        self.assertEqual(sorter.normalize("file", existing), "file_2")

    def test_unique_name_no_collision(self) -> None:
        self.assertEqual(sorter.normalize("fresh", {"other"}), "fresh")


# ===========================================================================
# 2. get_category
# ===========================================================================
class TestGetCategory(SorterTestBase):
    def test_known_categories(self) -> None:
        self.assertEqual(sorter.get_category("jpg"), "images")
        self.assertEqual(sorter.get_category("MP4"), "video")
        self.assertEqual(sorter.get_category("pdf"), "documents")
        self.assertEqual(sorter.get_category("mp3"), "audio")
        self.assertEqual(sorter.get_category("zip"), "archives")

    def test_case_insensitive(self) -> None:
        self.assertEqual(sorter.get_category("PnG"), "images")

    def test_unknown_extension_is_other(self) -> None:
        self.assertEqual(sorter.get_category("xyz"), sorter.OTHER_CATEGORY)
        self.assertEqual(sorter.get_category(""), sorter.OTHER_CATEGORY)


# ===========================================================================
# 3. make_unique_path
# ===========================================================================
class TestMakeUniquePath(SorterTestBase):
    def test_returns_same_when_free(self) -> None:
        path = sorter.make_unique_path(self.tmp, "a.txt")
        self.assertEqual(path, self.tmp / "a.txt")

    def test_appends_counter_on_collision(self) -> None:
        self.touch("a.txt")
        path = sorter.make_unique_path(self.tmp, "a.txt")
        self.assertEqual(path, self.tmp / "a_1.txt")


# ===========================================================================
# 4. move_file
# ===========================================================================
class TestMoveFile(SorterTestBase):
    def test_moves_into_category_folder(self) -> None:
        src = self.touch("photo.jpg")
        sorter.move_file(src, self.tmp, "images")
        self.assertFalse(src.exists())
        self.assertTrue((self.tmp / "images" / "photo.jpg").exists())

    def test_normalizes_cyrillic_name(self) -> None:
        src = self.touch("фото.jpg")
        sorter.move_file(src, self.tmp, "images")
        self.assertTrue((self.tmp / "images" / "foto.jpg").exists())


# ===========================================================================
# 5. handle_archive
# ===========================================================================
class TestHandleArchive(SorterTestBase):
    def test_extracts_valid_archive(self) -> None:
        archive = self.tmp / "data.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("inside.txt", "hello")
        sorter.handle_archive(archive, self.tmp)
        self.assertFalse(archive.exists())
        self.assertTrue((self.tmp / "archives" / "data" / "inside.txt").exists())

    def test_moves_corrupt_archive_as_is(self) -> None:
        archive = self.touch("broken.zip")
        sorter.handle_archive(archive, self.tmp)
        self.assertFalse(archive.exists())
        self.assertTrue((self.tmp / "archives" / "broken.zip").exists())


# ===========================================================================
# 6. process_folder
# ===========================================================================
class TestProcessFolder(SorterTestBase):
    def test_sorts_nested_tree_and_removes_empty_dirs(self) -> None:
        self.touch("note.txt")
        self.touch("clip.mp4")
        self.touch("sub/song.mp3")

        sorter.process_folder(self.tmp, self.tmp)

        self.assertTrue((self.tmp / "documents" / "note.txt").exists())
        self.assertTrue((self.tmp / "video" / "clip.mp4").exists())
        self.assertTrue((self.tmp / "audio" / "song.mp3").exists())
        self.assertFalse((self.tmp / "sub").exists())

    def test_unknown_extension_goes_to_other(self) -> None:
        self.touch("mystery.xyz")
        sorter.process_folder(self.tmp, self.tmp)
        self.assertTrue((self.tmp / sorter.OTHER_CATEGORY / "mystery.xyz").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)