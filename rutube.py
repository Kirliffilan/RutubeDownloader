import re
import requests


def get_headers():
    return {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://rutube.ru/"
    }


def api_get(url, params=None):
    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


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
    video_id = get_video_id(url)

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

    if season_match:
        season = int(
            season_match.group(1)
        )

    if episode_match:
        episode = int(
            episode_match.group(1)
        )

    show_name = re.sub(
        r"\s*\d+\s*сезон.*",
        "",
        title,
        flags=re.IGNORECASE
    ).strip()

    return {
        "id": video_id,
        "rutube_id": video_id,
        "title": title,
        "author_id": author_id,
        "author_name": author_name,
        "show_name": show_name,
        "season": season,
        "episode": episode,
        "url": url
    }