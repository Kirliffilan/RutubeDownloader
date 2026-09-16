import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from rutube import api_get
from utils import get_video_size


class Searcher:
    def __init__(self):
        self.stop = False

    def stop_search(self):
        self.stop = True

    def search_episode(self, show_name, author_id, season, episode, quality):
        if self.stop:
            return None

        query = f"{show_name} " f"{season} сезон " f"{episode} серия"

        try:
            data = api_get(
                "https://rutube.ru/api/search/video/",
                {"query": query, "page": 1, "limit": 10},
            )

        except Exception:
            return None

        for item in data.get("results", []):

            title = str(item.get("title", "")).strip()

            pattern = (
                rf"{re.escape(show_name)}"
                rf".*{season}\s*сезон"
                rf".*{episode}\s*серия"
            )

            if not re.search(pattern, title, re.IGNORECASE):
                continue

            author = item.get("author", {})

            item_author = None

            if isinstance(author, dict):
                item_author = author.get("id")

            if author_id and item_author and str(author_id) != str(item_author):
                continue

            video_id = item.get("id")

            if not video_id:
                continue

            url = f"https://rutube.ru/video/{video_id}/"

            size = get_video_size(url, quality)

            return {
                "show_name": show_name,
                "rutube_id": str(video_id),
                "url": url,
                "title": title,
                "season": season,
                "episode": episode,
                "size": size,
            }

        return None

    def find_seasons(self, video_info, settings, callback=None):
        self.stop = False

        show_name = video_info["show_name"]
        author_id = video_info["author_id"]

        seasons = {}
        tasks = []

        for season in range(1, settings["max_seasons"] + 1):

            for episode in range(1, settings["max_episodes"] + 1):

                tasks.append((season, episode))

        if callback:
            callback("log", f"Проверок: {len(tasks)}")

        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = []

            for season, episode in tasks:

                futures.append(
                    executor.submit(
                        self.search_episode,
                        show_name,
                        author_id,
                        season,
                        episode,
                        settings["quality"],
                    )
                )

            for future in as_completed(futures):

                if self.stop:
                    break

                result = future.result()

                if result:

                    season = result["season"]
                    episode = result["episode"]

                    if season not in seasons:
                        seasons[season] = {}

                    seasons[season][episode] = result

                    size_mb = result.get("size", 0) / 1024 / 1024

                    callback(
                        "log",
                        f"Найдена: {season} сезон {episode} серия | Размер: {size_mb:.0f} MB",
                    )

        if callback:
            count = sum(len(x) for x in seasons.values())

            total_size = sum(
                item.get("size", 0)
                for season in seasons.values()
                for item in season.values()
            )

            callback("log", f"Всего найдено: {count}")

            callback(
                "log",
                f"Общий размер найденных видео: {total_size / 1024 / 1024 / 1024:.2f} GB",
            )

        return seasons
