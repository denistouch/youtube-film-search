import builtins
import os

from dotenv import load_dotenv


def _get(name: str, default=None, _type: builtins = str):
    load_dotenv()
    if variable := os.environ.get(name):
        return _type(variable)

    return default


def _list(name: str, default=None) -> list[str]:
    if default is None:
        default = []

    if variable := _get(name, default):
        return variable.split(",")

    return default


YOUTUBE_API_KEY = _get("YOUTUBE_API_KEY")
YOUTUBE_MAX_COMMENTS = _get("YOUTUBE_MAX_COMMENTS", 20, int)
YOUTUBE_TIMEOUT_SECONDS = _get("YOUTUBE_TIMEOUT_SECONDS", 1, float)
YOUTUBE_CACHE_TTL_SECONDS = _get("YOUTUBE_CACHE_TTL_SECONDS", 86400, int)

AI_ANSWER_FORMAT = _get("AI_ANSWER_FORMAT", "Название (год)")
AI_DATA_SEPARATOR = _get("AI_DATA_SEPARATOR", "____")
AI_SYSTEM_PROMPT = _get("AI_SYSTEM_PROMPT", f"""
Я предоставлю тебе массив данных, я хочу чтобы ты проанализировал его и назвал мне фильм или сериал, 
который наиболее вероятно ему соответствует ему, если можно однозначно определить год, то укажи его обязательно в скобках.
Напоминаю, важно в ответе дать только название и при возможности год никакой другой информации быть не должно.
Уточняю, что название должно быть именно одно.
Символами {AI_DATA_SEPARATOR} я разделю данные.
Первым пойдёт название ролика, вторым описание, а дальше 20 наиболее релевантных комментариев.
Формат ответа: {AI_ANSWER_FORMAT}.
Есть сценарии в которых такой ответ дать невозможно, например, если ролик не является нарезкой из фильма, в таком случае
можешь дать вежливый ответ о том что не удаётся распознать фильм и кратко описать причины не более 10-15 слов. 
""")
AI_BASE_URL = _get("AI_BASE_URL", "http://localhost:1234").rstrip("/")
AI_MODEL = _get("AI_MODEL", "google/gemma-3n-e4b")
AI_TEMPERATURE = _get("AI_TEMPERATURE", 0.1, float)
AI_MAX_TOKENS = _get("AI_MAX_TOKENS", -1, int)
AI_STREAM = _get("AI_STREAM", False, bool)
AI_CACHE_TTL_SECONDS = _get("AI_CACHE_TTL_SECONDS", 3600, int)

TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_START_MESSAGE = _get("TELEGRAM_BOT_START_MESSAGE",
                                  "Привет, сюда можно присылать ссылки на нарезки фильмов на Youtube, а мы попробуем понять что это за кино.")
TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID = _get("TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID",
                                             "Не удалось определить идентификатор видео по переданной ссылке.")
TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_BY_ID = _get("TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID",
                                                "Не удалось найти видео по ссылке.")
TELEGRAM_BOT_ERROR_MODEL_UNAVAILABLE = _get("TELEGRAM_BOT_ERROR_MODEL_UNAVAILABLE",
                                            "К сожалению модель в данный момент недоступна.")
TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE = _get("TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE",
                                              "Не удалось подтвердить наличие фильма на кинопоиске.")
TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE = _get("TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE",
                                               "Мы нашли фильма на кинопоиске, но он неточный.")

KINOPOISK_API_KEY = _get("KINOPOISK_API_KEY")
KINOPOISK_API_BASE_URL = _get("KINOPOISK_API_BASE_URL", "https://api.kinopoisk.dev").rstrip("/")
KINOPOISK_CACHE_TTL_SECONDS = _get("KINOPOISK_CACHE_TTL_SECONDS", 86400, int)

MOVIE_NOT_APPROVE_THRESHOLD = _get('MOVIE_APPROVE_THRESHOLD', 50, int)
MOVIE_HALF_APPROVE_THRESHOLD = _get('MOVIE_APPROVE_THRESHOLD', 90, int)
