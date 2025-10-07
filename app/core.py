import re
import sys
import logging

import ai
import cache
import config
import kinopoisk
import log
import matcher
import throttling
import youtube
import karelia_pro

youtube_api = youtube.Api(
    config.YOUTUBE_API_KEY,
    throttling.RateLimiter(config.YOUTUBE_TIMEOUT_SECONDS),
    cache.Storage.restore(config.YOUTUBE_CACHE_TTL_SECONDS, 'youtube')
)
assistant_api = ai.Assistant(
    config.AI_SYSTEM_PROMPT,
    config.AI_BASE_URL,
    config.AI_MODEL,
    config.AI_TEMPERATURE,
    config.AI_MAX_TOKENS,
    config.AI_STREAM,
    cache.Storage.restore(config.AI_CACHE_TTL_SECONDS, 'ai')
)
kinopoisk_api = kinopoisk.Api(
    config.KINOPOISK_API_KEY,
    config.KINOPOISK_API_BASE_URL,
    cache.Storage.restore(config.KINOPOISK_CACHE_TTL_SECONDS, 'kinopoisk')
)
karelia_pro_api = karelia_pro.Api(
    cache.Storage.restore(config.KARELIA_PRO_CACHE_TTL_SECONDS, 'karelia_pro'),
    throttling.RateLimiter(config.KARELIA_PRO_TIMEOUT_SECONDS),
    config.KARELIA_PRO_BASE_URL
)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def prepare_answer(link: str, username: str, _id: str, provider: str = None) -> tuple[str | None, str | None]:
    if not (video_id := youtube.parse_video_id_by_link(link)):
        log.warning(mark_action(username, 'video_id not found'), _id)
        return None, config.TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID
    log.debug(mark_action(username, 'found video id'), _id, video_id)

    if not (summary := youtube_api.get_video_summary_by_id(video_id, config.YOUTUBE_MAX_COMMENTS, _id)):
        log.warning(mark_action(username, 'summary not build'), video_id, _id)
        return None, config.TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID
    log.debug(mark_action(username, 'fetch summary'), _id, summary)

    if not (assistant_movie := assistant_api.find_movie_by_summary(_wrap_assistant_json(summary), _id)):
        log.warning(mark_action(username, 'assistant not answer'), summary, _id)
        return None, config.TELEGRAM_BOT_ERROR_MODEL_UNAVAILABLE
    log.debug(mark_action(username, 'assistant answered'), _id, assistant_movie)

    movie, score = approve_movie(assistant_movie, config.MOVIE_HALF_APPROVE_THRESHOLD, _id)
    log.debug(_score_log_msg(assistant_movie, movie, score, username), video_id, _id)

    if score < config.MOVIE_NOT_APPROVE_THRESHOLD:
        return None, _build_not_approved_movie_msg(assistant_movie)

    if score < config.MOVIE_HALF_APPROVE_THRESHOLD:
        return None, _build_half_approved_movie_msg(assistant_movie, movie.name_with_year())

    return build_with_provider_answer(provider, movie)


def _score_log_msg(assistant_movie: str, movie: kinopoisk.Movie | None, score: int, username: str) -> str:
    return mark_action(
        username, f'ai:{assistant_movie} kinopoisk:{movie.name_with_year() if movie else ''} score:{score}')


def approve_movie(candidate: str, fast_approve_threshold: int, _id: str) -> tuple[kinopoisk.Movie | None, int]:
    movie, score = _get_kinopoisk_movie(candidate, _id)
    if score > fast_approve_threshold:
        return movie, score

    candidate_without_year = clean_year(candidate)
    if candidate_without_year == candidate:
        return movie, score

    movie_by_name, score_by_name = _get_kinopoisk_movie(candidate_without_year, _id)
    if score_by_name > score:
        return movie_by_name, score_by_name

    return movie, score


def get_hello_message() -> str:
    return config.TELEGRAM_BOT_START_MESSAGE


def get_telegram_bot_token() -> str:
    return config.TELEGRAM_BOT_TOKEN


def mark_action(username: str, action: str) -> str:
    return f'[{username}]: {action}'


def shutdown():
    youtube_api.shutdown()
    assistant_api.shutdown()
    kinopoisk_api.shutdown()
    karelia_pro_api.shutdown()


def clean_year(candidate):
    return re.sub(r' \(?\d+\)?', '', candidate)


def _build_not_approved_movie_msg(assistant_answer: str) -> str:
    return (config.TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE_TEMPLATE
            .replace(config.CORE_MESSAGES_AI_PLACEHOLDER, assistant_answer))


def _build_half_approved_movie_msg(assistant_answer: str, approver_answer) -> str:
    return (config.TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE_TEMPLATE
            .replace(config.CORE_MESSAGES_AI_PLACEHOLDER, assistant_answer)
            .replace(config.CORE_MESSAGES_APPROVER_PLACEHOLDER, approver_answer))


def _get_kinopoisk_movie(candidate: str, _id: str) -> tuple[kinopoisk.Movie | None, int]:
    movies = kinopoisk_api.movie_search(candidate, _id)
    if movie := movies[0] if len(movies) > 0 else None:
        score = 0
        for name in movie.names_with_year():
            score = max(matcher.calculate_match_score(candidate, name), score)

        return movie, score

    return None, 0


def _wrap_assistant_json(summary: youtube.VideoSummary) -> str:
    # todo move to summary
    return f'''
        "title": "{summary.title}",
        "description": "{summary.description}",
        "owner_comments": "{summary.owner_comments}",
        "top_comments": "{summary.relevant_comments}",
    '''


def map_kinopoisk_to_karelia_pro(kinopoisk_type: str) -> str:
    if kinopoisk_type in [kinopoisk.Movie.TYPE_CARTOON, kinopoisk.Movie.TYPE_ANIMATED_SERIES]:
        return karelia_pro.Content.TYPE_MULT
    elif kinopoisk_type in [kinopoisk.Movie.TYPE_TV_SERIES]:
        return karelia_pro.Content.TYPE_SERIAL
    elif kinopoisk_type in [kinopoisk.Movie.TYPE_ANIME]:
        return karelia_pro.Content.TYPE_ANIME
    else:
        return karelia_pro.Content.TYPE_VIDEO


def build_with_provider_answer(provider: str | None, movie: kinopoisk.Movie) -> tuple[str | None, str | None]:
    if provider == karelia_pro.PROVIDER:
        karelia_pro_content = karelia_pro_api.movie_search(movie.name(), map_kinopoisk_to_karelia_pro(movie.type))
        if karelia_pro_content:
            return f"{movie.as_text_with_link()}\n{karelia_pro_content.link()}", None
    return movie.as_text_with_link(), None


def get_provider(tg_id) -> str | None:
    if str(tg_id) in config.KARELIA_PRO_USERS:
        return karelia_pro.PROVIDER
    return None
