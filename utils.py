import os


def clean_filename(name):
    bad = '\\/:*?"<>|'

    for char in bad:
        name = name.replace(
            char,
            ""
        )

    return name.strip()


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(
            path,
            exist_ok=True
        )

    return path