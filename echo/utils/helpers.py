from datetime import datetime, timezone


def time_ago(timestamp: int) -> str:
    delta = datetime.now(timezone.utc) - datetime.fromtimestamp(timestamp, tz=timezone.utc)
    days = delta.days
    hours = delta.seconds // 3600
    mins = (delta.seconds % 3600) // 60

    if days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    elif mins > 0:
        return f"{mins}m"
    return "now"


def truncate_npub(npub: str, length: int = 12) -> str:
    if len(npub) <= length:
        return npub
    return f"{npub[:length // 2]}…{npub[-length // 2:]}"


def format_count(count: int) -> str:
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)
