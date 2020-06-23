from datetime import datetime
import pytz

from django.conf import settings


def unix_to_datetime_tz(timestamp):
    if not timestamp:
        return None
    timestamp = int(timestamp) if isinstance(timestamp, str) else timestamp
    local_tz = pytz.timezone(settings.TIME_ZONE)
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    local_dt = local_tz.normalize(utc_dt.astimezone(local_tz))
    return local_dt
