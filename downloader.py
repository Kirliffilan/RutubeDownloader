import os
import yt_dlp

from database import log_error, save_history
from utils import clean_filename


class Downloader:
    def __init__(self):
        self.stopped = False

    def stop_download(self):
        self.stopped = True

    def get_format(self, quality):
        if quality in ("best", "Максимальное"):
            return "bestvideo+bestaudio/best"

        try:
            quality = int(quality)
        except ValueError:
            return "bestvideo+bestaudio/best"

        return (
            f"bestvideo[height<={quality}]+bestaudio/"
            f"best[height<={quality}]"
        )

    def find_downloaded_file(self, folder, title):
        if not os.path.exists(folder):
            return None

        title = clean_filename(title).lower()

        for file in os.listdir(folder):
            if not file.lower().endswith(".mp4"):
                continue

            name = clean_filename(file).lower()

            if title in name:
                return os.path.join(folder, file)

        return None

    def format_speed(self, speed):
        if not speed:
            return ""

        return f"{speed / 1024 / 1024:.2f} MB/s"

    def format_eta(self, seconds):
        if seconds is None:
            return ""

        seconds = int(seconds)

        return f"{seconds // 60}:{seconds % 60:02d}"

    def progress_hook(self, callback):
        last_speed = ""
        last_eta = ""

        def hook(data):
            nonlocal last_speed, last_eta

            if self.stopped:
                raise Exception(
                    "Остановлено пользователем"
                )

            if data["status"] == "downloading":
                total = (
                    data.get("total_bytes")
                    or data.get("total_bytes_estimate")
                )

                if data.get("speed"):
                    last_speed = self.format_speed(
                        data["speed"]
                    )

                if data.get("eta") is not None:
                    last_eta = self.format_eta(
                        data["eta"]
                    )

                if total:
                    callback(
                        "progress",
                        {
                            "percent": (
                                data["downloaded_bytes"]
                                /
                                total
                                *
                                100
                            ),
                            "speed": last_speed,
                            "eta": last_eta
                        }
                    )

            elif data["status"] == "finished":
                callback(
                    "progress",
                    {
                        "percent": 100,
                        "speed": last_speed,
                        "eta": "0:00"
                    }
                )

                callback(
                    "log",
                    "Обработка файла..."
                )

        return hook

    def download_episode(self, item, settings, show_name, callback):
        if self.stopped:
            return False

        season = item["season"]
        episode = item["episode"]

        folder = os.path.join(
            settings["save_path"],
            show_name,
            f"{season} сезон"
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        if self.find_downloaded_file(
            folder,
            item["title"]
        ):
            callback(
                "log",
                f"Пропуск: {season} сезон {episode} серия"
            )

            return "skip"

        callback(
            "log",
            f"Скачивание: {season} сезон {episode} серия"
        )

        options = {
            "format": self.get_format(
                settings["quality"]
            ),
            "outtmpl": os.path.join(
                folder,
                "%(title)s.%(ext)s"
            ),
            "merge_output_format": "mp4",
            "continuedl": True,
            "retries": 30,
            "fragment_retries": 30,
            "concurrent_fragment_downloads": 16,
            "progress_hooks": [
                self.progress_hook(callback)
            ]
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download(
                    [item["url"]]
                )

        except Exception as e:
            if self.stopped:
                callback(
                    "log",
                    "Скачивание остановлено"
                )
            else:
                log_error(
                    str(e)
                )

                callback(
                    "log",
                    f"Ошибка: {e}"
                )

            return False

        if self.stopped:
            return False

        file = self.find_downloaded_file(
            folder,
            item["title"]
        )

        if file:
            save_history(
                item,
                file
            )

        return True

    def download_all(self, selected, settings, show_name, callback):
        self.stopped = False

        success = 0
        skipped = 0

        total = len(selected)

        for index, item in enumerate(selected, 1):
            if self.stopped:
                callback(
                    "log",
                    "Загрузка отменена"
                )

                break

            callback(
                "log",
                f"[{index}/{total}]"
            )

            result = self.download_episode(
                item,
                settings,
                show_name,
                callback
            )

            if result == "skip":
                skipped += 1

            elif result:
                success += 1

        callback(
            "progress",
            {
                "percent": 100,
                "speed": "",
                "eta": "0:00"
            }
        )

        callback(
            "log",
            f"Готово. Скачано: {success}, пропущено: {skipped}"
        )