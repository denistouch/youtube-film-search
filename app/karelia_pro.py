from dataclasses import dataclass

import requests

import cache
import throttling

_DOMAIN = 'karelia.pro'
PROVIDER = 'https://citylink.pro/'


@dataclass
class Content:
    TYPE_VIDEO = "video"
    TYPE_SERIAL = "serial"
    TYPE_ANIME = "anime"
    TYPE_MULT = "mult"

    def __init__(self, _id: int, _type: str, title: str):
        self.id = _id
        self.type = _type
        self.title = title

    def link(self):
        return f"http://{self.type}.{_DOMAIN}/updates#video_{str(self.id)}"


class Api:
    _SITE_BY_TYPE = {
        Content.TYPE_VIDEO: 1,
        Content.TYPE_SERIAL: 2,
        Content.TYPE_ANIME: 3,
        Content.TYPE_MULT: 5,
    }

    def __init__(self, storage: cache.Storage, limiter: throttling.RateLimiter, base_url: str):
        self._storage = storage
        self._limiter = limiter
        self._base_url = base_url

    def movie_search(self, query: str, _type: str, kp_id = None) -> Content | None:
        @throttling.with_limiter(self._limiter)
        def _search(q, t, kp):
            return self.perform_query(q, t, kp)

        return _search(query, _type, kp_id)

    def perform_query(self, query: str, _type: str, kp_id) -> Content | None:
        url = f"http://{self._base_url}/ajax/search/1"
        params = {
            "query": query,
            "site": str(self._SITE_BY_TYPE[_type]),
        }
        headers = {
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Referer": f"http://{_type}.{_DOMAIN}/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Host": f"{_type}.{_DOMAIN}",
        }

        @cache.with_cache(self._storage)
        def execute(_params):
            response = requests.get(url, params=_params, headers=headers, verify=False)
            response.raise_for_status()
            return response.json()

        response = execute(params)
        for content_data in response.get("videos", []):
            if str(content_data.get('kinopoiskId','')) == str(kp_id):
                return Content(
                    content_data.get('id'),
                    _type,
                    content_data.get('title'),
                )

        return None

    def shutdown(self):
        self._storage.archive()
