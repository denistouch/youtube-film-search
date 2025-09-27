import requests

import cache


class Movie:
    def __init__(self, _id: int, name: str, alternative_name: str | None, year: int):
        self.id = _id
        self.name = name
        self.alternative_name = alternative_name
        self.year = year

    def name_with_year(self) -> str:
        return f'{self.name if self.name else self.alternative_name} ({self.year})'

    def alternative_name_with_year(self) -> str:
        return f'{self.alternative_name if self.alternative_name else self.name} ({self.year})'

    def as_text_with_link(self) -> str:
        return f"{self.name_with_year()}\nhttps://www.kinopoisk.ru/film/{self.id}"


class Api:
    _api_key: str
    _base_url: str

    def __init__(self, api_key: str, base_url: str, storage: cache.Storage):
        self._api_key = api_key
        self._base_url = base_url
        self._storage = storage

    def movie_search(self, query: str, page: int = 1, limit: int = 10) -> list[Movie]:
        @cache.with_cache(self._storage)
        def execute(_query) -> list[Movie]:
            data = self._execute_request(query, page, limit)
            if not data["docs"]:
                return []

            movies = []
            for movie_data in data["docs"]:
                movies.append(_parse_movie_data(movie_data))

            return movies

        return execute(query)

    def _execute_request(self, query: str, page: int = 1, limit: int = 10) -> dict:
        return ((requests.get(f"{self._base_url}/v1.4/movie/search",
                              headers={
                                  "accept": "application/json",
                                  "X-API-KEY": self._api_key
                              },
                              params={
                                  "page": page,
                                  "limit": limit,
                                  "query": query
                              }))
                .json())


def _parse_movie_data(movie_data: dict) -> Movie:
    return Movie(
        movie_data.get("id", -1),
        movie_data.get("name"),
        movie_data.get("alternativeName"),
        movie_data.get("year"),
    )
