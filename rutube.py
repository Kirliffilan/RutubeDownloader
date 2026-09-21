import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import get_video_size

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://rutube.ru/"}


def api_get(url, params=None):
    last_error = None

    for _ in range(3):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            last_error = e
            time.sleep(2)

    raise last_error


def api_get_fast(url, params=None):
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=5)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def get_video_id(url):
    patterns = [r"/video/([a-zA-Z0-9_-]+)", r"video_id=([a-zA-Z0-9_-]+)"]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Не удалось определить ID видео")


def get_video_info(url):
    video_id = get_video_id(url)
    with ThreadPoolExecutor(max_workers=2) as executor:
        video_future = executor.submit(
            api_get, f"https://rutube.ru/api/video/{video_id}/"
        )
        serial_future = executor.submit(
            api_get_fast, f"https://rutube.ru/pangolin/api/web/serial/{video_id}"
        )
        data = video_future.result()
        serial_data = serial_future.result()

    title = data.get("title", "")
    author = data.get("author", {})

    if isinstance(author, dict):
        author_id = author.get("id")
        author_name = author.get("name", "")
    else:
        author_id = None
        author_name = ""

    season = None
    episode = None
    is_serial = False

    if serial_data and serial_data.get("results"):
        is_serial = True
        current_season = serial_data.get("current_season")
        if current_season:
            season = current_season
            season_data = api_get_fast(
                f"https://rutube.ru/pangolin/api/web/serial/{video_id}/{season}/",
                {"limit": 19, "offset": -2},
            )
            print("SEASON DATA")
            print(season_data)
            if season_data:
                for item in season_data.get("results", []):
                    if item.get("id") == video_id:
                        episode = item.get("episode")
                        break

    return {
        "id": video_id,
        "rutube_id": video_id,
        "url": url,
        "title": title,
        "author_id": author_id,
        "author_name": author_name,
        "show_name": title,
        "season": season,
        "episode": episode,
        "is_serial": is_serial,
    }


def search_video(query):
    return api_get(
        "https://rutube.ru/api/search/video/", {"query": query, "page": 1, "limit": 10}
    )


def is_serial(video_id):
    try:
        data = api_get(f"https://rutube.ru/pangolin/api/web/serial/{video_id}")
        return bool(data.get("results"))
    except Exception:
        return False


def get_season_episodes(video_id, season, limit):
    url = f"https://rutube.ru/pangolin/api/web/serial/{video_id}/{season}/"

    try:
        data = api_get(url, {"limit": limit, "offset": -2})
    except Exception:
        return []

    results = data.get("results", [])

    if not results:
        return []

    season_episodes = results.copy()
    next_url = data.get("next")

    while next_url:
        try:
            page = api_get(next_url)
        except Exception:
            break
        for item in page.get("results", []):
            if item["id"] not in [x["id"] for x in season_episodes]:
                season_episodes.append(item)
        next_url = page.get("next")

    return season_episodes


def get_serial_episodes(video_id, settings, callback=None):
    episodes = []
    max_seasons = settings.get("max_seasons", 20)
    limit = settings.get("max_episodes", 100)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(get_season_episodes, video_id, season, limit)
            for season in range(1, max_seasons + 1)
        ]
        for future in as_completed(futures):
            result = future.result()
            for item in result:
                if item["id"] not in [x["rutube_id"] for x in episodes]:
                    episodes.append(
                        {
                            "rutube_id": item["id"],
                            "url": item["video_url"],
                            "title": item["title"],
                            "season": item.get("season"),
                            "episode": item.get("episode"),
                            "show_name": item["title"],
                            "author_id": item["author"]["id"],
                            "author_name": item["author"]["name"],
                        }
                    )

    episodes.sort(key=lambda x: (x.get("season") or 999, x.get("episode") or 999))

    def check_size(item):
        try:
            size = get_video_size(item["url"], settings["quality"])
            item["size"] = size
            if callback:
                callback(
                    "log",
                    f"Проверена: {item['season']} сезон {item['episode']} серия | {size/1024/1024:.0f} MB",
                )
        except Exception:
            item["size"] = 0
        return item

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_size, item) for item in episodes]
        episodes = [future.result() for future in as_completed(futures)]

    episodes.sort(key=lambda x: (x.get("season") or 999, x.get("episode") or 999))
    total_size = sum(item.get("size", 0) for item in episodes)

    if callback:
        callback("log", f"Всего серий: {len(episodes)}")
        callback("log", f"Общий размер всех серий: {total_size/1024/1024/1024:.2f} GB")

    return episodes
