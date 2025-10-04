import logging
from typing import Callable
from strings import json

_TEST_PREFIX = 'test_'


def _build_expected_not_actual(expected, actual) -> str:
    return f'{json(expected)} != {json(actual)}'


def _build_assertion_error(_method, i, e, expected, actual):
    return f'{_method} [case #{i}] {str(e)} {_build_expected_not_actual(expected, actual)}'


def assert_equals_cases(cases, as_json=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            errors = []
            for i, declaration in enumerate(cases):
                if len(declaration) == 2:
                    declaration += [None]
                _args, expected, _message = declaration
                actual = func(_args)
                if as_json:
                    expected = json(expected)
                    actual = json(actual)
                try:
                    if _message:
                        assert expected == actual, _message
                    else:
                        assert expected == actual
                except AssertionError as e:
                    errors.append(AssertionError(_build_assertion_error(func.__name__, i, e, expected, actual)))

            return errors

        return wrapper

    return decorator


def run_tests(_globals: dict, tests_function_prefix=_TEST_PREFIX, logger: logging.Logger = None,
              shutdown_callback: Callable = None):
    if not logger:
        logger = logging.getLogger('tests')
    tests = []
    failed = []
    for key, value in _globals.items():
        if key.startswith(tests_function_prefix) and isinstance(value, Callable):
            tests.append([key.replace(tests_function_prefix, ''), value])

    for name, test in tests:
        _err = test()
        if _err:
            failed += _err

    if len(failed) != 0:
        logger.error('Tests ends with errors!')
        for failure in failed:
            logger.exception(repr(failure))
        _exit(1, shutdown_callback)

    logger.info('All tests passed!')
    _exit(0, shutdown_callback)


def _exit(result, callback):
    if callback:
        callback()
    exit(result)
