import copy
import os
import uuid

import ai
import config
import core
import test_lib
import serialize, files
from cache import Storage
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
    ['Шазам (2015)', ['Шазам! (2019)', 91]],
    ['Сёстры', ['Сёстры (2021)', 100]],
    ['Alice in Borderland (2020)', ['Алиса в Пограничье (2020)', 100]],
    ['Крысиные бега (2001)', ['Крысиные бега (2001)', 100]],
    ['НИКТО (2021)', ['Никто (2021)', 100]],
    ['911', ['911 (2022)', 100]],
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
    cache = Storage(name='tests')
    key = 'key'
    data = {'key': 'value'}
    cache.put('key', data, 30)
    file = files.build_storage_path(cache.name)
    cache.archive()
    assert os.path.exists(file)
    restored = Storage.restore(name='tests')
    assert restored.get(key) == data
    os.remove(file)
    assert not os.path.exists(file)

def test_cache_restore():
    cache = Storage.restore(name='ai')
    assert cache is not None


if __name__ == '__main__':
    test_lib.run_tests(copy.copy(globals()))
    core.shutdown()
