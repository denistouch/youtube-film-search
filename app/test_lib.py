import logging
from typing import Callable
from strings import json

_TEST_PREFIX = 'test_'


def _build_expected_not_actual(expected, actual) -> str:
    return f'{json(expected)} != {json(actual)}'


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
                _expected = json(expected)

                if isinstance(_args, list):
                    actual = func(*_args)
                else:
                    actual = func(_args)

                _actual = json(actual)
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
