import os
import yt_dlp


def get_video_size(url, quality):
    if quality in ("best", "Максимальное"):
        height = None
    else:
        height = int(quality)

    options = {"quiet": True, "no_warnings": True}

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

            duration = info.get("duration")

            if not duration:
                return 0

            video_bitrate = 0
            audio_bitrate = 0

            formats = info.get("formats", [])

            selected_video = None
            selected_audio = None

            for fmt in formats:
                fmt_height = fmt.get("height")

                if height and fmt_height and fmt_height > height:
                    continue

                if fmt.get("vcodec") != "none":
                    if not selected_video or (fmt.get("tbr") or 0) > (
                        selected_video.get("tbr") or 0
                    ):
                        selected_video = fmt

                if fmt.get("acodec") != "none":
                    if not selected_audio or (fmt.get("abr") or 0) > (
                        selected_audio.get("abr") or 0
                    ):
                        selected_audio = fmt

            if selected_video:
                video_bitrate = selected_video.get("tbr") or 0

            if selected_audio:
                audio_bitrate = (
                    selected_audio.get("abr") or selected_audio.get("tbr") or 0
                )

            bitrate = video_bitrate + audio_bitrate

            if bitrate:
                return int(bitrate * 1000 * duration / 8)

            return 0

    except Exception as e:
        print("SIZE ERROR:", e)

        return 0


def clean_filename(name):
    bad = '\\/:*?"<>|'

    for char in bad:
        name = name.replace(char, "")

    return name.strip()


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    return path
