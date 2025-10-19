import time


class RateLimiter:
    _last_execute: float = 0
    _executions: int = 0
    _ttl = 0

    def __init__(self, timeout_between_requests):
        self._ttl = timeout_between_requests

    def touch(self):
        self._last_execute = time.time()
        self._executions += 1

    def wait(self):
        from_last_request = time.time() - self._last_execute
        if from_last_request < self._ttl:
            time.sleep(self._ttl - from_last_request)


def with_limiter(limiter: RateLimiter):
    def decorator(func):
        def wrapper(*args, **kwargs):
            limiter.wait()
            result = func(*args, **kwargs)
            limiter.touch()

            return result

        return wrapper

    return decorator
