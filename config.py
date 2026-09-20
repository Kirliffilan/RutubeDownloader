import json
import os
import sys


def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    return os.path.join(get_base_path(), "config.json")


def get_default_save_path():
    return os.path.join(os.path.expanduser("~"), "Videos", "RutubeDownloader")


def get_default_settings():
    return {
        "save_path": get_default_save_path(),
        "quality": "Максимальное",
        "max_seasons": 5,
        "max_episodes": 10,
    }


def get_settings():
    path = get_config_path()

    if not os.path.exists(path):
        settings = get_default_settings()
        save_settings(settings)

        return settings

    try:
        with open(path, "r", encoding="utf-8") as file:
            settings = json.load(file)

    except Exception:
        settings = get_default_settings()
        save_settings(settings)

        return settings

    default = get_default_settings()

    for key, value in default.items():
        if key not in settings:
            settings[key] = value

    return settings


def save_settings(settings):
    path = get_config_path()

    with open(path, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)
