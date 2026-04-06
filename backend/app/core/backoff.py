from datetime import timedelta


def calculate_backoff(retry_count: int) -> timedelta:
    seconds = 2 ** retry_count
    return timedelta(seconds=seconds)
