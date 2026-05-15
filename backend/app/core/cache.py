from functools import lru_cache
from typing import Any
import time
# key -> (expires_at, value)
_BOOKS_LIST_CACHE: dict[tuple, tuple[float, Any]] = {}
DEFAULT_TTL_SECONDS = 30


def _books_list_key(
    user_id: int,
    title: str | None,
    author: str | None,
    category_id: int | None,
    sort_by: str | None,
    sort_dir: str,
    page: int,
    page_size: int,
):
    return (
        user_id,
        title,
        author,
        category_id,
        sort_by,
        sort_dir,
        page,
        page_size,
    )


@lru_cache(maxsize=256)
def cached_books_key(
    title: str | None,
    author: str | None,
    sort_by: str | None,
    sort_dir: str,
    page: int,
    page_size: int,
):
    """
    Cache key helper (pure + hashable).
    lru_cache avoids recomputing the tuple.
    """
    return (title, author, sort_by, sort_dir, page, page_size)


def get_books_list_cache(
    user_id: int,
    title: str | None,
    author: str | None,
    category_id: int | None,
    sort_by: str | None,
    sort_dir: str,
    page: int,
    page_size: int,
):

    key = _books_list_key(
        user_id,
        title,
        author,
        category_id,
        sort_by,
        sort_dir,
        page,
        page_size,
    )
    item = _BOOKS_LIST_CACHE.get(key)
    if not item:
        return None
    expires_at, value = item
    if time.time() > expires_at:
        _BOOKS_LIST_CACHE.pop(key, None)
        return None
    return value


def set_books_list_cache(
    user_id: int,
    title: str | None,
    author: str | None,
    category_id: int | None,
    sort_by: str | None,
    sort_dir: str,
    page: int,
    page_size: int,
    value,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
):
    key = _books_list_key(
        user_id,
        title,
        author,
        category_id,
        sort_by,
        sort_dir,
        page,
        page_size,
    )
    _BOOKS_LIST_CACHE[key] = (time.time() + ttl_seconds, value)


def invalidate_books_list_cache(user_id: int | None = None):
    """
    Optional improvement:
    - invalidate all cache
    - or invalidate per user
    """
    if user_id is None:
        _BOOKS_LIST_CACHE.clear()
        return
    keys_to_delete = [k for k in _BOOKS_LIST_CACHE if k[0] == user_id]
    for k in keys_to_delete:
        _BOOKS_LIST_CACHE.pop(k, None)
