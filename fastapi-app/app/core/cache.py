from functools import lru_cache

@lru_cache(maxsize=128)
def cached_books_key(title: str | None, author: str | None, sort_by: str | None):
    """
    Cache key helper.
    Iru_cache caches...."""
    return (title, author, sort_by)

