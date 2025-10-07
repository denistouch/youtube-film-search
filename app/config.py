import builtins
import os

from dotenv import load_dotenv

_DOTENV_PATH = '.env'

load_dotenv(_DOTENV_PATH)


def _get(name: str, default=None, _type: builtins = str):
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

AI_SYSTEM_PROMPT = _get("AI_SYSTEM_PROMPT")
AI_BASE_URL = _get("AI_BASE_URL", "").rstrip("/")
AI_MODEL = _get("AI_MODEL")
AI_TEMPERATURE = _get("AI_TEMPERATURE", _type=float)
AI_MAX_TOKENS = _get("AI_MAX_TOKENS", _type=int)
AI_STREAM = bool(_get("AI_STREAM", _type=int))
AI_CACHE_TTL_SECONDS = _get("AI_CACHE_TTL_SECONDS", _type=int)

TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_START_MESSAGE = _get("TELEGRAM_BOT_START_MESSAGE", "hello_message")
TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID = _get("TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID", "video_id_not_found_message")
TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_BY_ID = _get("TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_BY_ID", "video_not_found_message")
TELEGRAM_BOT_ERROR_MODEL_UNAVAILABLE = _get("TELEGRAM_BOT_ERROR_MODEL_UNAVAILABLE", "model_unavailable_message")
TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE_TEMPLATE = _get("TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE_TEMPLATE",
                                                       "movie_not_approved_template")
TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE_TEMPLATE = _get("TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE_TEMPLATE",
                                                        "movie_half_approved_template")

KINOPOISK_API_KEY = _get("KINOPOISK_API_KEY")
KINOPOISK_API_BASE_URL = _get("KINOPOISK_API_BASE_URL", "").rstrip("/")
KINOPOISK_CACHE_TTL_SECONDS = _get("KINOPOISK_CACHE_TTL_SECONDS", _type=int)

MOVIE_NOT_APPROVE_THRESHOLD = _get('MOVIE_NOT_APPROVE_THRESHOLD', _type=int)
MOVIE_HALF_APPROVE_THRESHOLD = _get('MOVIE_HALF_APPROVE_THRESHOLD', _type=int)

CORE_MESSAGES_AI_PLACEHOLDER = _get('CORE_MESSAGES_AI_PLACEHOLDER')
CORE_MESSAGES_APPROVER_PLACEHOLDER = _get('CORE_MESSAGES_APPROVER_PLACEHOLDER')

KARELIA_PRO_USERS = set(_get('KARELIA_PRO_USERS', '').split(','))
KARELIA_PRO_CACHE_TTL_SECONDS = _get('KARELIA_PRO_CACHE_TTL_SECONDS', _type=int)
KARELIA_PRO_TIMEOUT_SECONDS = _get('KARELIA_PRO_TIMEOUT_SECONDS', _type=int)
KARELIA_PRO_BASE_URL = _get('KARELIA_PRO_BASE_URL')
