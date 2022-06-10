from datetime import datetime
from zoneinfo import ZoneInfo


def get_utc_now() -> datetime:
    return datetime.now(tz=ZoneInfo("UTC"))
