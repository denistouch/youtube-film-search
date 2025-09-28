import logging
import sys

import ai
import cache
import config
import kinopoisk
import matcher
import throttling
import youtube

youtube_api = youtube.Api(
    config.YOUTUBE_API_KEY,
    throttling.RateLimiter(config.YOUTUBE_TIMEOUT_SECONDS),
    cache.Storage(config.YOUTUBE_CACHE_TTL_SECONDS)
)
assistant = ai.Assistant(
    config.AI_SYSTEM_PROMPT,
    config.AI_BASE_URL,
    config.AI_MODEL,
    config.AI_TEMPERATURE,
    config.AI_MAX_TOKENS,
    config.AI_STREAM,
    cache.Storage(config.AI_CACHE_TTL_SECONDS)
)
kinopoisk_api = kinopoisk.Api(
    config.KINOPOISK_API_KEY,
    config.KINOPOISK_API_BASE_URL,
    cache.Storage(config.AI_CACHE_TTL_SECONDS)
)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def prepare_answer(link: str, username: str) -> tuple[str | None, str | None]:
    if not (video_id := youtube.parse_video_id_by_link(link)):
        logging.warning(f'{username}: video_id not found')
        return None, config.TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID

    if not (summary := youtube_api.get_video_summary_by_id(video_id, config.YOUTUBE_MAX_COMMENTS)):
        logging.warning(f'{username}: summary not build', video_id)
        return None, config.TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID

    if not (assistant_movie := assistant.find_film_name_by_summary(wrap_assistant_json(summary))):
        logging.warning(f'{username}: assistant not answer', summary)
        return None, config.TELEGRAM_BOT_ERROR_MODEL_UNAVAILABLE

    kinopoisk_movie, score = approve_movie(assistant_movie)
    if score < config.MOVIE_NOT_APPROVE_THRESHOLD:
        logging.warning(f'{username}: ai:{assistant_movie} kinopoisk:{kinopoisk_movie.name_with_year()} score:{score}')
        return None, build_not_approved_movie_msg(assistant_movie)

    if score < config.MOVIE_HALF_APPROVE_THRESHOLD:
        logging.warning(f'{username}: ai:{assistant_movie} kinopoisk:{kinopoisk_movie.name_with_year()} score:{score}')
        return None, build_half_approved_movie_msg(assistant_movie, kinopoisk_movie.name_with_year())

    logging.info(f'{username}: ai:{assistant_movie} kinopoisk:{kinopoisk_movie.name_with_year()} score:{score}')
    return kinopoisk_movie.as_text_with_link(), None


def approve_movie(candidate: str) -> tuple[kinopoisk.Movie | None, int]:
    movies = kinopoisk_api.movie_search(candidate)
    if movie := movies[0] if len(movies) > 0 else None:
        return movie, max(matcher.calculate_match_score(candidate, movie.name_with_year()),
                          matcher.calculate_match_score(candidate, movie.alternative_name_with_year()))

    return None, 0


def build_not_approved_movie_msg(assistant_answer: str) -> str:
    return f"{config.TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE}\nМнение AI: {assistant_answer}"


def build_half_approved_movie_msg(assistant_answer: str, kinopoisk_answer) -> str:
    return f"{config.TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE}\nМнение AI: {assistant_answer}\nКинопоиск:{kinopoisk_answer}"


def get_hello_message() -> str:
    return config.TELEGRAM_BOT_START_MESSAGE


def get_telegram_bot_token() -> str:
    return config.TELEGRAM_BOT_TOKEN


def wrap_assistant_json(summary: youtube.VideoSummary) -> str:
    return f'''
        "title": "{summary.title}",
        "description": "{summary.description}",
        "owner_comments": "{summary.owner_comments}",
        "top_comments": "{summary.relevant_comments}",
    '''
