import config
import strings


def not_approved_movie_msg(assistant_answer: str) -> str:
    return (config.TELEGRAM_BOT_ERROR_NOT_APPPROVED_MOVIE_TEMPLATE
            .replace(config.CORE_MESSAGES_AI_PLACEHOLDER, assistant_answer))


def half_approved_movie_msg(assistant_answer: str, approver_answer) -> str:
    return (config.TELEGRAM_BOT_ERROR_HALF_APPPROVED_MOVIE_TEMPLATE
            .replace(config.CORE_MESSAGES_AI_PLACEHOLDER, assistant_answer)
            .replace(config.CORE_MESSAGES_APPROVER_PLACEHOLDER, approver_answer))


def approved_movie(kinopoisk_name: str, kinopoisk_link: str, provider_link: str | None = None) -> str:
    msg = f"{kinopoisk_name}\n{kinopoisk_link}"
    if provider_link:
        msg += f"\n{provider_link}"
    return msg


def score_log_msg(assistant_movie: str, movie: str, score: int, username: str) -> str:
    return strings.username_action(
        username, f'ai:{assistant_movie} kinopoisk:{movie} score:{score}')
