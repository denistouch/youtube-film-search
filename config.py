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
AI_DATA_SEPARATOR = _get("AI_DATA_SEPARATOR", " | ")
AI_HIGH_RELEVANT_DATA_MARKER = _get("AI_HIGH_RELEVANT_DATA_MARKER", "\n!! Данные от первоисточника !!\n")
AI_LOW_RELEVANT_DATA_MARKER = _get("AI_LOW_RELEVANT_DATA_MARKER", "\n!! Непроверенные данные !!\n")
AI_SYSTEM_PROMPT = _get("AI_SYSTEM_PROMPT", f"""
Ты - эксперт по фильмам, специализирующийся на извлечении ключевой информации из неструктурированных текстовых данных. 
Твоя задача - вытащить название фильма, указанное в предоставленном тексте.

Я предоставлю тебе массив данных, которые идут по убыванию ценности я хочу чтобы ты проанализировал его и назвал мне фильм или сериал, который наиболее вероятно ему соответствует, если можно однозначно определить год, то укажи его в скобках.
Символами {AI_DATA_SEPARATOR} я разделю данные внутри группы.

Крайне важно соблюдать следующие правила:
1. **Название фильма:** Идентифицируй основное название фильма, которое явно или косвенно упоминается в тексте.
2. **Формат ответа:** Предоставь ответ только в следующем формате: `{AI_ANSWER_FORMAT}`. Никаких дополнительных пояснений или приветствий не требуется. Уточняю, что название должно быть именно одно. Не называй год, если не можешь определить его наверняка.
3. **Использовать данные**: Используй предоставленные данные, отдавая предпочтение "{AI_HIGH_RELEVANT_DATA_MARKER}" и обращаясь к "{AI_LOW_RELEVANT_DATA_MARKER}" в случае необходимости, для поиска названия фильма.  Не используй внешние источники.
4. **Лаконичность:** В ответе важно дать только название и при возможности год, никакой другой информации быть не должно.

Есть сценарии в которых такой ответ дать невозможно, например, если ролик не является нарезкой из фильма, в таком случае
можешь дать вежливый ответ о том что не удаётся распознать фильм и кратко описать причины не более 10-15 слов.
""")
AI_BASE_URL = _get("AI_BASE_URL").rstrip("/")
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
TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE = _get("TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE", "movie_not_approved_message")
TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE = _get("TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE", "movie_half_approved_message")

KINOPOISK_API_KEY = _get("KINOPOISK_API_KEY")
KINOPOISK_API_BASE_URL = _get("KINOPOISK_API_BASE_URL").rstrip("/")
KINOPOISK_CACHE_TTL_SECONDS = _get("KINOPOISK_CACHE_TTL_SECONDS", _type=int)

MOVIE_NOT_APPROVE_THRESHOLD = _get('MOVIE_NOT_APPROVE_THRESHOLD', _type=int)
MOVIE_HALF_APPROVE_THRESHOLD = _get('MOVIE_HALF_APPROVE_THRESHOLD', _type=int)
