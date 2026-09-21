import os
import shutil
import yt_dlp
from database import log_error, save_history
from utils import clean_filename


class Downloader:
    def __init__(self):
        self.stop = False
        self.last_percent = 0
        self.last_speed = ""
        self.last_eta = ""
        self.last_size = 0

    def stop_download(self):
        self.stop = True

    def get_format(self, quality):
        if quality in ("best", "Максимальное"):
            return "bestvideo+bestaudio/best"
        try:
            quality = int(quality)
        except Exception:
            return "bestvideo+bestaudio/best"
        return (
            f"bestvideo[height<={quality}]" + "+bestaudio/" f"best[height<={quality}]"
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

    def clear_fragments(self, folder):
        if not os.path.exists(folder):
            return
        for file in os.listdir(folder):
            if ".part-Frag" in file:
                try:
                    os.remove(os.path.join(folder, file))
                except Exception:
                    pass

    def format_speed(self, speed):
        if not speed:
            return ""
        return f"{speed/1024/1024:.2f} MB/s"

    def format_eta(self, seconds):
        if seconds is None:
            return ""
        seconds = int(seconds)
        minutes = seconds // 60
        sec = seconds % 60
        return f"{minutes}:{sec:02d}"

    def progress_hook(self, callback):
        def hook(data):
            if self.stop:
                raise yt_dlp.utils.DownloadError("Остановлено пользователем")
            if data["status"] == "downloading":
                total = data.get("total_bytes") or data.get("total_bytes_estimate")
                if data.get("speed"):
                    self.last_speed = self.format_speed(data.get("speed"))
                if data.get("eta") is not None:
                    self.last_eta = self.format_eta(data.get("eta"))
                if total:
                    self.last_size = total
                    self.last_percent = data["downloaded_bytes"] / total * 100
                    callback(
                        "progress",
                        {
                            "percent": self.last_percent,
                            "speed": self.last_speed,
                            "eta": self.last_eta,
                            "size": self.last_size,
                            "free": shutil.disk_usage(
                                os.path.dirname(data.get("filename", ""))
                            ).free,
                        },
                    )
            elif data["status"] == "finished":
                if self.stop:
                    return
                callback(
                    "progress",
                    {
                        "percent": self.last_percent,
                        "speed": self.last_speed,
                        "eta": "0:00",
                        "size": self.last_size,
                        "free": shutil.disk_usage(
                            os.path.dirname(data.get("filename", ""))
                        ).free,
                    },
                )
                callback("log", "Обработка файла...")

        return hook

    def download_episode(self, item, settings, show_name, mode, callback):
        if self.stop:
            return False

        season = item.get("season")
        episode = item.get("episode")

        if mode == "Сериал":
            folder = os.path.join(settings["save_path"], show_name, f"{season} сезон")
            filename = f"{season}_{episode} {item['title']}.%(ext)s"
        else:
            video_folder = settings.get("video_folder", "")

            if video_folder:
                folder = os.path.join(settings["save_path"], video_folder)
            else:
                folder = settings["save_path"]

            filename = f"{item['title']}.%(ext)s"

        os.makedirs(folder, exist_ok=True)

        estimated_size = item.get("size", 0)

        if estimated_size:
            free_space = shutil.disk_usage(folder).free

            callback("log", f"Расчётный размер: {estimated_size / 1024 / 1024:.2f} MB")

            callback("log", f"Свободное место: {free_space / 1024 / 1024:.2f} MB")

            if free_space < estimated_size:
                callback("log", "Недостаточно места на диске. Загрузка отменена.")
                return False

        if self.find_downloaded_file(folder, item["title"]):
            callback("log", "Файл уже существует")
            return "skip"

        self.clear_fragments(folder)

        if mode == "Сериал":
            callback("log", f"Скачивание: {season} сезон {episode} серия")
        else:
            callback("log", "Скачивание видео")

        options = {
            "format": self.get_format(settings["quality"]),
            "outtmpl": os.path.join(folder, filename),
            "skip_unavailable_fragments": False,
            "break_on_reject": True,
            "merge_output_format": "mp4",
            "continuedl": True,
            "socket_timeout": 60,
            "fragment_timeout": 60,
            "retries": 50,
            "fragment_retries": 50,
            "file_access_retries": 10,
            "concurrent_fragment_downloads": 16,
            "hls_use_mpegts": False,
            "nopart": False,
            "keepvideo": False,
            "progress_hooks": [self.progress_hook(callback)],
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                if self.stop:
                    return False

                ydl.download([item["url"]])

        except yt_dlp.utils.DownloadError as e:
            if self.stop:
                callback("log", "Скачивание остановлено")
                return False

            raise e

        except Exception as e:
            if self.stop:
                callback("log", "Скачивание остановлено")
            else:
                log_error(str(e))
                callback("log", f"Ошибка: {e}")

            return False

        file = self.find_downloaded_file(folder, item["title"])

        if file:
            save_history(item, file, settings)

        return True

    def download_all(self, selected, settings, show_name, mode, callback):
        self.stop = False
        success = 0
        skipped = 0
        total = len(selected)

        for index, item in enumerate(selected, 1):
            if self.stop:
                callback("log", "Загрузка отменена")
                break

            callback("log", f"[{index}/{total}]")

            result = self.download_episode(item, settings, show_name, mode, callback)

            if result == "skip":
                skipped += 1
            elif result:
                success += 1
            elif result is False:
                break

        if not self.stop:
            callback(
                "progress",
                {
                    "percent": 100,
                    "speed": "",
                    "eta": "0:00",
                    "size": None,
                    "free": shutil.disk_usage(settings["save_path"]).free,
                },
            )

        if self.stop:
            callback("log", "Загрузка остановлена")
        else:
            callback("log", f"Готово. Скачано: {success}, пропущено: {skipped}")
