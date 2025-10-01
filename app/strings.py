import abc
from collections import abc
from dataclasses import is_dataclass, asdict
from types import SimpleNamespace
from typing import Any


def json(obj: Any) -> Any:
    """Рекурсивно преобразует любой объект в JSON-совместимый вид."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [json(item) for item in obj]
    if isinstance(obj, dict):
        return {json(k): json(v) for k, v in obj.items()}
    if hasattr(obj, '__dict__'):
        # Объект с __dict__
        return {k: json(v) for k, v in vars(obj).items() if not k.startswith('_') and v is not None}
    if hasattr(obj, '__slots__'):
        # Объект с __slots__
        return {k: json(getattr(obj, k)) for k in obj.__slots__ if not k.startswith('_')}
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, SimpleNamespace):
        return {k: json(v) for k, v in obj.__dict__.items()}
    if isinstance(obj, abc.Mapping):
        return {json(k): json(v) for k, v in obj.items()}
    if isinstance(obj, abc.Iterable) and not isinstance(obj, (str, bytes)):
        return [json(item) for item in obj]

    return str(obj)
