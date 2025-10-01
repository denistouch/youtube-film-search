import abc
import logging
from collections import abc
from dataclasses import is_dataclass, asdict
from types import SimpleNamespace
from typing import Any
from typing import Callable

_TEST_PREFIX = 'test_'


def _jsonable(obj: Any) -> Any:
    """Рекурсивно преобразует любой объект в JSON-совместимый вид."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_jsonable(item) for item in obj]
    if isinstance(obj, dict):
        return {_jsonable(k): _jsonable(v) for k, v in obj.items()}
    if hasattr(obj, '__dict__'):
        # Объект с __dict__
        return {k: _jsonable(v) for k, v in vars(obj).items() if not k.startswith('_')}
    if hasattr(obj, '__slots__'):
        # Объект с __slots__
        return {k: _jsonable(getattr(obj, k)) for k in obj.__slots__ if not k.startswith('_')}
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, SimpleNamespace):
        return {k: _jsonable(v) for k, v in obj.__dict__.items()}
    if isinstance(obj, abc.Mapping):
        return {_jsonable(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, abc.Iterable) and not isinstance(obj, (str, bytes)):
        return [_jsonable(item) for item in obj]

    return str(obj)


def _build_expected_not_actual(expected, actual) -> str:
    return f'{_jsonable(expected)} != {_jsonable(actual)}'


def _build_assertion_error(_method, i, e, expected, actual):
    return f'{_method} [case #{i}] {str(e)} {_build_expected_not_actual(expected, actual)}'


def assert_equals_cases(cases):
    def decorator(func):
        def wrapper(*args, **kwargs):
            errors = []
            for i, declaration in enumerate(cases):
                if len(declaration) == 2:
                    declaration += [None]
                _args, expected, _message = declaration
                _expected = _jsonable(expected)

                if isinstance(_args, list):
                    actual = func(*_args)
                else:
                    actual = func(_args)

                _actual = _jsonable(actual)
                try:
                    if _message:
                        assert _expected == _actual, _message
                    else:
                        assert _expected == _actual
                except AssertionError as e:
                    errors.append(AssertionError(_build_assertion_error(func.__name__, i, e, _expected, _actual)))

            return errors

        return wrapper

    return decorator


def run_tests(_globals: dict, tests_function_prefix=_TEST_PREFIX, logger: logging.Logger = None):
    if not logger:
        logger = logging.getLogger('tests')
    tests = []
    failed = []
    for key, value in _globals.items():
        if key.startswith(tests_function_prefix) and isinstance(value, Callable):
            tests.append([key.replace(tests_function_prefix, ''), value])

    for name, test in tests:
        failed += test()

    if len(failed) != 0:
        logger.error('Tests ends with errors!')
        for failure in failed:
            logger.exception(repr(failure))
        exit(1)

    logger.info('All tests passed!')
    exit(0)
