import pickle
import base64
from typing import Any


def serialize_base64(obj: Any) -> str:
    return base64.b64encode(serialize_bytes(obj)).decode('utf-8')


def deserialize_base64(data: str) -> Any:
    return deserialize_bytes(base64.b64decode(data.encode('utf-8')))


def serialize_bytes(obj: Any) -> bytes:
    return pickle.dumps(obj)


def deserialize_bytes(data: bytes | None) -> Any:
    if data is None:
        return None
    return pickle.loads(data)
