import sys
import shutil
import zipfile
import tarfile
import gzip
from pathlib import Path

# ── Таблиця транслітерації ──────────────────────────────────────────────────
CYRILLIC_TO_LATIN = {
    'а': 'a',  'б': 'b',  'в': 'v',  'г': 'g',  'д': 'd',
    'е': 'e',  'є': 'ie', 'ж': 'zh', 'з': 'z',  'и': 'y',
    'і': 'i',  'ї': 'yi', 'й': 'y',  'к': 'k',  'л': 'l',
    'м': 'm',  'н': 'n',  'о': 'o',  'п': 'p',  'р': 'r',
    'с': 's',  'т': 't',  'у': 'u',  'ф': 'f',  'х': 'kh',
    'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch','ь': '',
    'ю': 'yu', 'я': 'ya',
    # Великі
    'А': 'A',  'Б': 'B',  'В': 'V',  'Г': 'G',  'Д': 'D',
    'Е': 'E',  'Є': 'Ie', 'Ж': 'Zh', 'З': 'Z',  'И': 'Y',
    'І': 'I',  'Ї': 'Yi', 'Й': 'Y',  'К': 'K',  'Л': 'L',
    'М': 'M',  'Н': 'N',  'О': 'O',  'П': 'P',  'Р': 'R',
    'С': 'S',  'Т': 'T',  'У': 'U',  'Ф': 'F',  'Х': 'Kh',
    'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch','Ь': '',
    'Ю': 'Yu', 'Я': 'Ya',
}

# ── Категорії файлів ────────────────────────────────────────────────────────
CATEGORIES = {
    'images':    {'JPEG', 'PNG', 'JPG', 'SVG', 'GIF', 'BMP', 'WEBP'},
    'video':     {'AVI', 'MP4', 'MOV', 'MKV', 'FLV', 'WMV'},
    'documents': {'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'ODT'},
    'audio':     {'MP3', 'OGG', 'WAV', 'AMR', 'FLAC', 'AAC'},
    'archives':  {'ZIP', 'GZ', 'TAR'},
}

# Службові папки, які скрипт створює сам — їх не чіпаємо
SERVICE_FOLDERS = {'images', 'video', 'documents', 'audio', 'archives', 'other'}


# ── Функція normalize ───────────────────────────────────────────────────────
def normalize(name: str) -> str:
    """
    Транслітерує кириличні символи та замінює
    всі «проблемні» символи на підкреслення.
    """
    result = []
    for char in name:
        if char in CYRILLIC_TO_LATIN:
            result.append(CYRILLIC_TO_LATIN[char])
        elif char.isalnum():          # латинські літери і цифри — залишаємо
            result.append(char)
        else:
            result.append('_')        # будь-який інший символ → '_'
    return ''.join(result)


# ── Визначення категорії файлу ──────────────────────────────────────────────
def get_category(file: Path) -> str:
    ext = file.suffix.lstrip('.').upper()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return 'other'


# ── Обробники для кожного типу ──────────────────────────────────────────────
def handle_image(file: Path, base: Path) -> None:
    move_file(file, base / 'images')

def handle_video(file: Path, base: Path) -> None:
    move_file(file, base / 'video')

def handle_document(file: Path, base: Path) -> None:
    move_file(file, base / 'documents')

def handle_audio(file: Path, base: Path) -> None:
    move_file(file, base / 'audio')

def handle_other(file: Path, base: Path) -> None:
    move_file(file, base / 'other')

def handle_archive(file: Path, base: Path) -> None:
    """Розпаковує архів у папку archives/<ім'я_архіву>."""
    dest = base / 'archives' / normalize(file.stem)
    dest.mkdir(parents=True, exist_ok=True)
    try:
        if file.suffix.lower() == '.zip':
            with zipfile.ZipFile(file, 'r') as z:
                z.extractall(dest)
        elif file.suffix.lower() == '.tar':
            with tarfile.open(file, 'r') as t:
                t.extractall(dest)
        elif file.suffix.lower() == '.gz':
            out_name = dest / file.stem   # ім'я без .gz
            with gzip.open(file, 'rb') as gz_in, open(out_name, 'wb') as out:
                shutil.copyfileobj(gz_in, out)
        print(f'  [archive] Розпаковано: {file.name} → {dest}')
        file.unlink()                    # видаляємо оригінальний архів
    except Exception as e:
        print(f'  [archive] Помилка розпакування {file.name}: {e}')


HANDLERS = {
    'images':    handle_image,
    'video':     handle_video,
    'documents': handle_document,
    'audio':     handle_audio,
    'archives':  handle_archive,
    'other':     handle_other,
}


# ── Допоміжна функція переміщення з нормалізацією імені ────────────────────
def move_file(file: Path, dest_folder: Path) -> None:
    dest_folder.mkdir(parents=True, exist_ok=True)
    new_name = normalize(file.stem) + file.suffix   # суфікс (розширення) не змінюємо
    dest = dest_folder / new_name

    # Якщо файл із такою назвою вже є — додаємо лічильник
    counter = 1
    while dest.exists():
        dest = dest_folder / f'{normalize(file.stem)}_{counter}{file.suffix}'
        counter += 1

    shutil.move(str(file), str(dest))
    print(f'  [{dest_folder.name}] {file.name} → {dest.name}')


# ── Рекурсивна обробка папки ────────────────────────────────────────────────
def process_folder(folder: Path, base: Path) -> None:
    """
    Рекурсивно обходить папку.
    base — коренева папка, що передається під час першого виклику;
    потрібна, щоб правильно формувати шляхи до категорійних підпапок.
    """
    for item in list(folder.iterdir()):   # list() — знімок, бо вміст змінюється

        # Службові папки пропускаємо
        if item.is_dir() and item.name in SERVICE_FOLDERS and folder == base:
            continue

        if item.is_dir():
            process_folder(item, base)          # ← рекурсія

            # Видаляємо порожню папку після обробки
            try:
                item.rmdir()
                print(f'  [dir] Видалено порожню папку: {item.name}')
            except OSError:
                pass  # папка не порожня — залишаємо

        elif item.is_file():
            category = get_category(item)
            HANDLERS[category](item, base)


# ── Точка входу ─────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) != 2:
        print('Використання: python sort.py <шлях_до_папки>')
        sys.exit(1)

    target = Path(sys.argv[1]).resolve()

    if not target.exists() or not target.is_dir():
        print(f'Помилка: папка "{target}" не існує.')
        sys.exit(1)

    print(f'Починаємо сортування папки: {target}\n')
    process_folder(target, target)
    print('\nГотово! ✅')


if __name__ == '__main__':
    main()
