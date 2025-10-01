import logging
import re
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
        logging.warning(mark_action(username, 'video_id not found'))
        return None, config.TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID

    if not (summary := youtube_api.get_video_summary_by_id(video_id, config.YOUTUBE_MAX_COMMENTS)):
        logging.warning(mark_action(username, 'summary not build'), video_id)
        return None, config.TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID

    if not (assistant_movie := assistant.find_movie_by_summary(_wrap_assistant_json(summary))):
        logging.warning(mark_action(username, 'assistant not answer'), summary)
        return None, config.TELEGRAM_BOT_ERROR_MODEL_UNAVAILABLE

    movie, score = approve_movie(assistant_movie, config.MOVIE_HALF_APPROVE_THRESHOLD)
    logging.debug(_score_log_msg(assistant_movie, movie, score, username), video_id)
    if score < config.MOVIE_NOT_APPROVE_THRESHOLD:
        return None, _build_not_approved_movie_msg(assistant_movie)

    if score < config.MOVIE_HALF_APPROVE_THRESHOLD:
        return None, _build_half_approved_movie_msg(assistant_movie, movie.name_with_year())

    return movie.as_text_with_link(), None


def _score_log_msg(assistant_movie: str, movie: kinopoisk.Movie | None, score: int, username: str) -> str:
    return mark_action(
        username, f'ai:{assistant_movie} kinopoisk:{movie.name_with_year() if movie else ''} score:{score}')


def approve_movie(candidate: str, fast_approve_threshold: int) -> tuple[kinopoisk.Movie | None, int]:
    movie, score = _get_kinopoisk_movie(candidate)
    if score > fast_approve_threshold:
        return movie, score

    candidate_without_year = _clean_year(candidate)
    if candidate_without_year == candidate:
        return None, 0

    movie_by_name, score_by_name = _get_kinopoisk_movie(candidate_without_year)
    if score_by_name > score:
        return movie_by_name, score_by_name

    return movie, score


def get_hello_message() -> str:
    return config.TELEGRAM_BOT_START_MESSAGE


def get_telegram_bot_token() -> str:
    return config.TELEGRAM_BOT_TOKEN


def mark_action(username: str, action: str) -> str:
    return f'[{username}]: {action}'


def _clean_year(candidate):
    return re.sub(r'\(?\d+\)?', '', candidate)


def _build_not_approved_movie_msg(assistant_answer: str) -> str:
    return (config.TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE_TEMPLATE
            .replace(config.CORE_MESSAGES_AI_PLACEHOLDER, assistant_answer))


def _build_half_approved_movie_msg(assistant_answer: str, approver_answer) -> str:
    return (config.TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE_TEMPLATE
            .replace(config.CORE_MESSAGES_AI_PLACEHOLDER, assistant_answer)
            .replace(config.CORE_MESSAGES_APPROVER_PLACEHOLDER, approver_answer))


def _get_kinopoisk_movie(candidate: str) -> tuple[kinopoisk.Movie | None, int]:
    movies = kinopoisk_api.movie_search(candidate)
    if movie := movies[0] if len(movies) > 0 else None:
        return movie, max(matcher.calculate_match_score(candidate, movie.name_with_year()),
                          matcher.calculate_match_score(candidate, movie.alternative_name_with_year()))

    return None, 0


def _wrap_assistant_json(summary: youtube.VideoSummary) -> str:
    return f'''
        "title": "{summary.title}",
        "description": "{summary.description}",
        "owner_comments": "{summary.owner_comments}",
        "top_comments": "{summary.relevant_comments}",
    '''
