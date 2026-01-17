from functools import lru_cache
from typing import Any
import time
#key -> (expires_at, value)
_BOOKS_LIST_CACHE: dict[str, tuple[float, Any]] ={}
DEFAULT_TTL_SECONDS = 30

def _books_list_key(title: str | None, author: str | None, sort_by: str | None) -> str:
    return f"title={title}|author={author}|sort_by={sort_by}"


@lru_cache(maxsize=128)
def cached_books_key(title: str | None, author: str | None, sort_by: str | None):
    """
    Cache key helper.
    Iru_cache caches...."""
    return (title, author, sort_by)


def get_books_list_cache(title:str | None, author:str |None, sort_by:str | None):
    key = _books_list_key(title, author, sort_by)
    item = _BOOKS_LIST_CACHE.get(key)
    if not item:
        return None
    
    expires_at, value = item 
    
    if time.time() > expires_at: 
        _BOOKS_LIST_CACHE.pop(key, None)
        return None
    
    return value


def set_books_list_cache(
        title: str | None,
        author: str | None,
        sort_by:str | None,
        value,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
):
    key = _books_list_key(title, author, sort_by)
    _BOOKS_LIST_CACHE[key] = (time.time() + ttl_seconds, value)


def invalidate_books_list_cache():
    _BOOKS_LIST_CACHE.clear()


