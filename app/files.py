import os

_STORAGE_PATH = '/app/storage'


def save_file(filename, data: bytes):
    with open(filename, 'wb') as f:
        f.write(data)


def read_file(filename) -> bytes | None:
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as f:
        return f.read()


def build_storage_path(name: str) -> str:
    return f'{_STORAGE_PATH}/{name}.cache'
