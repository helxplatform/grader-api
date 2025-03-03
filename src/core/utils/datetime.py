from datetime import datetime
from zoneinfo import ZoneInfo

def get_now_with_tzinfo():
    return datetime.now(ZoneInfo("UTC"))