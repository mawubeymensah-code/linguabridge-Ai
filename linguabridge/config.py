"""Server-only configuration, with environment variables taking priority."""
import os
from collections.abc import Callable


def read_setting(name: str, default: str = "", secrets_get: Callable | None = None) -> str:
    value = os.environ.get(name)
    if value:
        return value
    if secrets_get is not None:
        try:
            value = secrets_get(name, default)
        except (FileNotFoundError, KeyError):
            return default
        if isinstance(value, str) and value:
            return value
    return default
