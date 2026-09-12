import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from rutube import api_get


class Searcher:
    def __init__(self):
        self.stopped = False

    def stop_search(self):
        self.stopped = True

    def search_episode(self, show_name, author_id, season, episode):
        if self.stopped:
            return None

        query = (
            f"{show_name} "
            f"{season} сезон "
            f"{episode} серия"
        )

        try:
            data = api_get(
                "https://rutube.ru/api/search/video/",
                {
                    "query": query,
                    "page": 1,
                    "limit": 10
                }
            )

        except Exception:
            return None

        for item in data.get("results", []):

            title = str(
                item.get("title", "")
            ).strip()

            pattern = (
                rf"{re.escape(show_name)}"
                rf".*{season}\s*сезон"
                rf".*{episode}\s*серия"
            )

            if not re.search(
                pattern,
                title,
                re.IGNORECASE
            ):
                continue

            author = item.get(
                "author",
                {}
            )

            item_author = None

            if isinstance(author, dict):
                item_author = author.get("id")

            if author_id and item_author and str(author_id) != str(item_author):
                continue

            video_id = item.get("id")

            if not video_id:
                continue

            return {
                "show_name": show_name,
                "rutube_id": str(video_id),
                "url": f"https://rutube.ru/video/{video_id}/",
                "title": title,
                "season": season,
                "episode": episode,
            }

        return None

    def find_seasons(self, video_info, settings, callback=None):
        self.stopped = False

        show_name = video_info["show_name"]
        author_id = video_info["author_id"]

        seasons = {}
        tasks = []

        for season in range(
            1,
            settings["max_seasons"] + 1
        ):
            for episode in range(
                1,
                settings["max_episodes"] + 1
            ):
                tasks.append(
                    (
                        season,
                        episode
                    )
                )

        if callback:
            callback(
                "log",
                f"Проверок: {len(tasks)}"
            )

        with ThreadPoolExecutor(
            max_workers=10
        ) as executor:

            futures = []

            for season, episode in tasks:
                futures.append(
                    executor.submit(
                        self.search_episode,
                        show_name,
                        author_id,
                        season,
                        episode
                    )
                )

            for future in as_completed(futures):

                if self.stopped:
                    break

                result = future.result()

                if result:
                    season = result["season"]
                    episode = result["episode"]

                    if season not in seasons:
                        seasons[season] = {}

                    seasons[season][episode] = result

                    if callback:
                        callback(
                            "log",
                            f"Найдена: {season} сезон {episode} серия"
                        )

        if callback:
            count = sum(
                len(x)
                for x in seasons.values()
            )

            callback(
                "log",
                f"Всего найдено: {count}"
            )

        return seasons