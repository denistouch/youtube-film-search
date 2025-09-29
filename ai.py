import re

import requests

import cache


def normalize_answer(answer: str) -> str:
    normalized = answer.replace("\n", '')

    if not re.search(r".* ?\(?\d{4}\)?$", normalized):
        normalized = re.sub(r" \(.*\)$", "", normalized).strip()

    return normalized


class _Api:
    _ROLE_ASSISTANT = "assistant"
    _ROLE_SYSTEM = "system"
    _ROLE_USER = "user"

    _base_url: str
    _model: str
    _temperature: float
    _max_tokens: int
    _stream: bool
    _storage: cache.Storage

    def __init__(self,
                 base_url: str,
                 model: str,
                 temperature: float,
                 max_tokens: int,
                 stream: bool,
                 storage: cache.Storage):
        self._base_url = base_url
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._stream = stream
        self._storage = storage

    def answer(self, prompt: str, system_prompt: str = None) -> str:
        @cache.with_cache(self._storage)
        def execute(_prompt) -> str:
            try:
                request = self._build_request(_prompt, system_prompt)
                response = self._execute_request(request)

                return self._parse_response(response)
            except requests.exceptions.ConnectionError as e:
                raise AssistantException("Connection Error", AssistantException.CODE_MODEL_UNAVAILABLE)

        return execute(prompt)

    def _execute_request(self, json_data: dict) -> dict:
        return (requests.post(f"{self._base_url}/v1/chat/completions",
                              headers={"Content-Type": "application/json"},
                              json=json_data)
                .json())

    def _build_request(self, prompt: str, system_prompt: str = None) -> dict:
        request = {
            "model": self._model,
            "messages": [
                self._build_message(self._ROLE_USER, prompt)
            ],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": self._stream,
        }

        if system_prompt:
            request["messages"] = [self._build_message(self._ROLE_SYSTEM, system_prompt)] + request["messages"]

        return request

    @staticmethod
    def _parse_response(response: dict) -> str:
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")

    @staticmethod
    def _build_message(role: str, content: str) -> dict:
        return {
            "role": role,
            "content": content,
        }


class Assistant:
    _system_prompt: str = None
    _api: _Api = None

    def __init__(self,
                 system_prompt: str,
                 base_url: str,
                 model: str,
                 temperature: float,
                 max_tokens: int,
                 stream: bool,
                 storage: cache.Storage,
                 ):
        self._system_prompt = system_prompt
        self.api = _Api(
            base_url,
            model,
            temperature,
            max_tokens,
            stream,
            storage
        )

    def find_movie_by_summary(self, unescape_json: str, post_process: bool = True) -> str | None:
        try:
            answer = self.api.answer(f'```{unescape_json}```', self._system_prompt)
            if post_process:
                return normalize_answer(answer)

            return answer
        except AssistantException:
            return None


class AssistantException(Exception):
    CODE_MODEL_UNAVAILABLE = 410
    reason: str
    code: int

    def __init__(self, reason: str, code: int):
        self.reason = reason
        self.code = code
