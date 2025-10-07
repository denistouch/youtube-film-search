import copy
import os
import uuid

import ai
import config
import core
import test_lib
import serialize, files
import cache
from karelia_pro import Content
from kinopoisk import Movie


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
    return core.prepare_answer(url, 'username', str(uuid.uuid4()))


@test_lib.assert_equals_cases([
    ['Шазам (2019)', ['Шазам! (2019)', 92]],
    ['Сёстры', ['Сёстры (2021)', 100]],
    ['Alice in Borderland (2020)', ['Алиса в Пограничье (2020)', 100]],
    ['Крысиные бега (2001)', ['Крысиные бега (2001)', 100]],
    ['НИКТО (2021)', ['Никто (2021)', 100]],
    ['911', ['911 (2022)', 100]],
    ['Дом Гиннесса (2025)', ['Дом Гиннессов (2025)', 89]],
    ['ЛЕГО Шазам: Магия и монстры (2020)', ['ЛЕГО Шазам: Магия и монстры (2020)', 100]],
    ['Les Sisters (2017)', ['Сёстры (2017)', 100]],
    ['Атака титанов (2013)', ['Атака титанов (2013)', 100]],
])
def test_core_approve_movie(candidate: str, fast_approve_threshold: int = config.MOVIE_HALF_APPROVE_THRESHOLD):
    movie, score = core.approve_movie(candidate, fast_approve_threshold, str(uuid.uuid4()))
    return movie.name_with_year(), score


@test_lib.assert_equals_cases([
    ['simple string', 'simple string'],
    [{'key': 'value'}, {'key': 'value'}],
    [['a', 1, {1, 2, 3}, {'a': 'b', 'c': ['d', 'e']}], ['a', 1, {1, 2, 3}, {'a': 'b', 'c': ['d', 'e']}]],
    [Movie(1, ['Название'], 2015), Movie(1, ['Название'], 2015)],
], False)
def test_serialize(data):
    serialized = serialize.serialize_bytes(data)
    return serialize.deserialize_bytes(serialized)


def test_cache_stored():
    storage = cache.Storage(name='tests')
    key = 'key'
    data = {'key': 'value'}
    storage.put('key', data, 30)
    file = files.build_storage_path(storage.name)
    storage.archive()
    assert os.path.exists(file)
    restored = cache.Storage.restore(name='tests')
    assert restored.get(key) == data
    os.remove(file)
    assert not os.path.exists(file)


def _test_cache_restore():
    storage = cache.Storage.restore(name='kinopoisk')
    assert storage is not None

@test_lib.assert_equals_cases([
    ['Шазам (2015)', 'Шазам'],
    ['Сёстры', 'Сёстры'],
    ['Alice in Borderland (2020)', 'Alice in Borderland'],
    ['Крысиные бега (2001)', 'Крысиные бега'],
    ['НИКТО (2021)', 'НИКТО'],
])
def test_clean_year(candidate):
    return core.clean_year(candidate)


@test_lib.assert_equals_cases([
    [['F1', Content.TYPE_VIDEO], 'http://video.karelia.pro/updates#video_46597'],
    [['Игра престолов', Content.TYPE_SERIAL], 'http://serial.karelia.pro/updates#video_14810'],
    [['Атака титанов', Content.TYPE_ANIME], 'http://anime.karelia.pro/updates#video_17379'],
    [['Гадкий я', Content.TYPE_MULT], 'http://mult.karelia.pro/updates#video_12076'],
])
def test_karelia_pro(data):
    candidate, _type = data
    actual = core.karelia_pro_api.movie_search(candidate, _type)
    return actual.link()


@test_lib.assert_equals_cases([
    ['6415316438', core.karelia_pro.PROVIDER],
    ['1054879386', core.karelia_pro.PROVIDER],
    ['1', None],
])
def test_get_provider(tg_id):
    return core.get_provider(tg_id)


@test_lib.assert_equals_cases([
    [None, core.karelia_pro.Content.TYPE_VIDEO],
    [core.kinopoisk.Movie.TYPE_MOVIE, core.karelia_pro.Content.TYPE_VIDEO],
    [core.kinopoisk.Movie.TYPE_CARTOON, core.karelia_pro.Content.TYPE_MULT],
    [core.kinopoisk.Movie.TYPE_ANIMATED_SERIES, core.karelia_pro.Content.TYPE_MULT],
    [core.kinopoisk.Movie.TYPE_TV_SERIES, core.karelia_pro.Content.TYPE_SERIAL],
    [core.kinopoisk.Movie.TYPE_ANIME, core.karelia_pro.Content.TYPE_ANIME],
])
def test_map_content_types(kinopoisk_type):
    return core.map_kinopoisk_to_karelia_pro(kinopoisk_type)


@test_lib.assert_equals_cases([
    [
        [None, Movie(1, ['Игра престолов'], 2024, core.kinopoisk.Movie.TYPE_TV_SERIES)],
        f"Игра престолов (2024)\nhttps://www.kinopoisk.ru/film/1"
    ],
    [
        [core.karelia_pro.PROVIDER, Movie(1, ['Игра престолов'], 2024, core.kinopoisk.Movie.TYPE_TV_SERIES)],
        f"Игра престолов (2024)\nhttps://www.kinopoisk.ru/film/1\nhttp://serial.karelia.pro/updates#video_14810"
    ]
])
def test_build_with_provider(data):
    provider, movie = data
    return core.build_with_provider_answer(provider, movie)[0]


if __name__ == '__main__':
    test_lib.run_tests(copy.copy(globals()), shutdown_callback=core.shutdown)
