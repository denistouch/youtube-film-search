import time
import hashlib

import files, serialize


def _md5_hash(input_string) -> str:
    return hashlib.md5(input_string.encode('utf-8')).hexdigest()


def _key_by_args(*args, **kwargs) -> str:
    args_key_parts = [str(arg) for arg in args]
    args_key = "_".join(args_key_parts)

    kwargs_key_parts = []
    for key, value in sorted(kwargs.items()):
        kwargs_key_parts.append(f"{key}-{value}")
    kwargs_key = "_".join(kwargs_key_parts)

    if args_key and kwargs_key:
        return f"{args_key}-{kwargs_key}"
    elif args_key:
        return args_key
    elif kwargs_key:
        return kwargs_key
    else:
        return ""


class Storage:
    _vault = None
    _ttl = 0

    def __init__(self, default_key_timeout=0, name: str = 'storage'):
        self._vault = {}
        self._ttl = default_key_timeout
        self.name = name

    def put(self, key, data, ttl=0):
        if ttl == 0:
            ttl = self._ttl
        self._vault[key] = _StorageItem(data, ttl)

    def get(self, key, default=None):
        item = self._vault.get(key, None)
        if isinstance(item, _StorageItem):
            if item.is_expired():
                del self._vault[key]
            return item.extract()
        return default

    def archive(self):
        files.save_file(files.build_storage_path(self.name), serialize.serialize_bytes(self))

    @staticmethod
    def restore(default_key_timeout=0, name: str = 'storage'):
        storage = serialize.deserialize_bytes(files.read_file(files.build_storage_path(name)))
        if storage is not None:
            storage._ttl = default_key_timeout
            return storage

        return Storage(default_key_timeout=default_key_timeout, name=name)


def with_cache(storage: Storage):
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = _md5_hash(_key_by_args(*args, **kwargs))
            cached = storage.get(key)

            if cached is not None:
                return cached

            data = func(*args, **kwargs)
            storage.put(key, data)
            return data

        return wrapper

    return decorator


class _StorageItem:
    _data = None
    _expired_at = None

    def __init__(self, data, ttl=0):
        self._data = data
        if ttl != 0:
            self._expired_at = time.time() + ttl

    def is_expired(self) -> bool:
        if self._expired_at:
            return time.time() > self._expired_at
        return True

    def extract(self):
        return self._data
