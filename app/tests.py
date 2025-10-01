import copy

import ai
import config
import core
import kinopoisk
import test_lib


@test_lib.assert_equals_cases([
    ["Сёстры (неопределён)", "Сёстры"],
    ["Сёстры (2014)", "Сёстры (2014)"],
    ["Сёстры 2014", "Сёстры 2014"],
])
def test_ai_normalize(before_normalization):
    return ai.normalize_answer(before_normalization)


@test_lib.assert_equals_cases([
    [['https://youtube.com/shorts/yFqdgT_224o?si=GYy5PkJdMneReVsR', 'username'],
     ('Американская семейка (2009)\nhttps://www.kinopoisk.ru/film/472329', None)],
])
def test_core_prepare_answer(url, username):
    return core.prepare_answer(url, username)


@test_lib.assert_equals_cases([
    ['Шазам (2015)', (kinopoisk.Movie(840372, 'Шазам!', 'Shazam!', 2019), 91)],
    ['Сёстры', (kinopoisk.Movie(4527915, 'Сёстры', '', 2021), 100)],
])
def test_core_approve_movie(candidate: str, fast_approve_threshold: int = config.MOVIE_HALF_APPROVE_THRESHOLD):
    return core.approve_movie(candidate, fast_approve_threshold)


if __name__ == '__main__':
    test_lib.run_tests(copy.copy(globals()))
