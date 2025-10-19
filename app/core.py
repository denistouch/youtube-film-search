import sys
import logging

import ai
import cache
import config
import kinopoisk
import log
import matcher
import messages
import strings
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
        log.warning(strings.username_action(username, 'video_id not found'), _id)
        return None, config.TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID
    log.debug(strings.username_action(username, 'found video id'), _id, video_id)

    if not (summary := youtube_api.get_video_summary_by_id(video_id, config.YOUTUBE_MAX_COMMENTS, _id)):
        log.warning(strings.username_action(username, 'summary not build'), video_id, _id)
        return None, config.TELEGRAM_BOT_ERROR_NOT_FOUND_VIDEO_ID
    log.debug(strings.username_action(username, 'fetch summary'), _id, summary)

    if not (assistant_movie := assistant_api.find_movie_by_summary(summary.json(), _id)):
        log.warning(strings.username_action(username, 'assistant not answer'), summary, _id)
        return None, config.TELEGRAM_BOT_ERROR_MODEL_UNAVAILABLE
    log.debug(strings.username_action(username, 'assistant answered'), _id, assistant_movie)

    movie, score = approve_movie(assistant_movie, config.MOVIE_HALF_APPROVE_THRESHOLD, _id)
    log.debug(messages.score_log_msg(
        assistant_movie,
        movie.name_with_year() if movie else '',
        score,
        username
    ), video_id, _id)

    if score < config.MOVIE_NOT_APPROVE_THRESHOLD:
        return None, messages.not_approved_movie_msg(assistant_movie)

    if score < config.MOVIE_HALF_APPROVE_THRESHOLD:
        return None, messages.half_approved_movie_msg(assistant_movie, movie.name_with_year())

    return build_with_provider_answer(provider, movie)


def approve_movie(candidate: str, fast_approve_threshold: int, _id: str) -> tuple[kinopoisk.Movie | None, int]:
    movie, score = get_kinopoisk_movie(candidate, _id)
    if score > fast_approve_threshold:
        return movie, score

    candidate_without_year = strings.clean_year(candidate)
    if candidate_without_year == candidate:
        return movie, score

    movie_by_name, score_by_name = get_kinopoisk_movie(candidate_without_year, _id)
    if score_by_name > score:
        return movie_by_name, score_by_name

    return movie, score


def get_hello_message() -> str:
    return config.TELEGRAM_BOT_START_MESSAGE


def get_telegram_bot_token() -> str:
    return config.TELEGRAM_BOT_TOKEN


def shutdown():
    youtube_api.shutdown()
    assistant_api.shutdown()
    kinopoisk_api.shutdown()
    karelia_pro_api.shutdown()


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
        content = karelia_pro_api.movie_search(movie.name(), map_kinopoisk_to_karelia_pro(movie.type), movie.id)
        if content:
            return messages.approved_movie(movie.name_with_year(), movie.link(), content.link()), None
    return messages.approved_movie(movie.name_with_year(), movie.link()), None


def get_provider(tg_id) -> str | None:
    if str(tg_id) in config.KARELIA_PRO_USERS:
        return karelia_pro.PROVIDER
    return None


def get_kinopoisk_movie(candidate: str, _id: str) -> tuple[kinopoisk.Movie | None, int]:
    movies = kinopoisk_api.movie_search(candidate, _id)
    if movie := movies[0] if len(movies) > 0 else None:
        score = 0
        for name in movie.names_with_year():
            score = max(matcher.calculate_match_score(candidate, name), score)

        return movie, score

    return None, 0
