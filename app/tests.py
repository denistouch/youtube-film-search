import copy

import ai
import config
import core
import kinopoisk
import test_lib


@test_lib.assert_equals_cases([
    ["Сёстры (неопределён)", "Сёстры"],
    ["Сёстры (2014)", "Сёстры (2014)"],
    ["Какая то длинная строка, которая не содержит цифры", "Какая то длинная строка, которая не содержит цифры"],
])
def test_ai_normalize(before_normalization):
    return ai.normalize_answer(before_normalization)


@test_lib.assert_equals_cases([
    ['https://youtube.com/shorts/yFqdgT_224o?si=GYy5PkJdMneReVsR',
     ('Американская семейка (2009)\nhttps://www.kinopoisk.ru/film/472329', None)],
])
def test_core_prepare_answer(url):
    return core.prepare_answer(url, 'username')


@test_lib.assert_equals_cases([
    ['Шазам (2015)', ['Шазам! (2019)', 91]],
    ['Сёстры', ['Сёстры (2021)', 100]],
    ['Alice in Borderland (2020)', ['Алиса в Пограничье (2020)', 100]],
    ['Крысиные бега (2001)', ['Крысиные бега (2001)', 100]],
    ['НИКТО (2021)', ['Никто (2021)', 100]],
])
def test_core_approve_movie(candidate: str, fast_approve_threshold: int = config.MOVIE_HALF_APPROVE_THRESHOLD):
    movie, score = core.approve_movie(candidate, fast_approve_threshold)
    return movie.name_with_year(), score


if __name__ == '__main__':
    test_lib.run_tests(copy.copy(globals()))
