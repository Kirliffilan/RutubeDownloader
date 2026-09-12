import re
import time
import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://rutube.ru/"
}


def api_get(url, params=None):
    last_error = None

    for _ in range(3):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            last_error = e

            time.sleep(2)

    raise last_error


def get_video_id(url):
    patterns = [
        r"/video/([a-zA-Z0-9_-]+)",
        r"video_id=([a-zA-Z0-9_-]+)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            url
        )

        if match:
            return match.group(1)

    raise ValueError(
        "Не удалось определить ID видео"
    )


def get_video_info(url):
    video_id = get_video_id(
        url
    )

    data = api_get(
        f"https://rutube.ru/api/video/{video_id}/"
    )

    title = data.get(
        "title",
        ""
    )

    author = data.get(
        "author",
        {}
    )

    if isinstance(author, dict):
        author_id = author.get(
            "id"
        )

        author_name = author.get(
            "name",
            ""
        )

    else:
        author_id = None
        author_name = ""

    season_match = re.search(
        r"(\d+)\s*сезон",
        title,
        re.IGNORECASE
    )

    episode_match = re.search(
        r"(\d+)\s*серия",
        title,
        re.IGNORECASE
    )

    season = None
    episode = None

    if season_match and episode_match:
        season = int(
            season_match.group(1)
        )

        episode = int(
            episode_match.group(1)
        )

    if season and episode:
        show_name = re.sub(
            r"\s*\d+\s*сезон.*",
            "",
            title,
            flags=re.IGNORECASE
        ).strip()

    else:
        show_name = title.strip()

    return {
        "id": video_id,
        "rutube_id": video_id,
        "url": url,
        "title": title,
        "author_id": author_id,
        "author_name": author_name,
        "show_name": show_name,
        "season": season,
        "episode": episode
    }


def search_video(query):
    return api_get(
        "https://rutube.ru/api/search/video/",
        {
            "query": query,
            "page": 1,
            "limit": 10
        }
    )