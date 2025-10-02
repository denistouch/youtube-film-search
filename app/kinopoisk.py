from dataclasses import dataclass

import log

import requests

import cache


@dataclass
class Movie:
    def __init__(self, _id: int, names: list, year: int):
        self.id = _id
        self.names = names
        self.year = year

    def names_with_year(self) -> list[str]:
        names = []
        for name in self.names:
            names.append(f'{name} ({self.year})')

        return names

    def name_with_year(self) -> str:
        return self.names_with_year()[0]

    def as_text_with_link(self) -> str:
        return f"{self.name_with_year()}\nhttps://www.kinopoisk.ru/film/{self.id}"


class Api:
    _api_key: str
    _base_url: str

    def __init__(self, api_key: str, base_url: str, storage: cache.Storage):
        self._api_key = api_key
        self._base_url = base_url
        self._storage = storage

    def movie_search(self, query: str, _id: str, page: int = 1, limit: int = 10) -> list[Movie]:
        @cache.with_cache(self._storage)
        def execute(_query) -> list[Movie]:
            data = self._execute_request(_query, page, limit)
            movies = []
            for movie_data in data.get("docs", []):
                movies.append(_parse_movie_data(movie_data))

            return movies

        try:
            return execute(query)
        except Exception as e:
            log.exception(e, _id)
            return []

    def shutdown(self):
        self._storage.archive()

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
    alternative_names = [
                            movie_data.get("name", ''),
                            movie_data.get("alternativeName", ''),
                            movie_data.get("enName", '')
                        ] + [
                            item.get("name", '') for item in movie_data['names']
                        ]
    return Movie(
        movie_data.get("id", -1),
        [name for name in alternative_names if name],
        movie_data.get("year")
    )
