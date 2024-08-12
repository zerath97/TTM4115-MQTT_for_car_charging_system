from datetime import datetime



def is_valid_time(d: datetime):
    ''' 
    Checks if a datetime is valid. 
    For this application, a valid datetime is defined as being either exactly HH:30 or HH:00.
    '''
    if d.minute != 0 and d.minute != 30:
        return False
    if d.second != 0:
        return False
    if d.microsecond != 0:
        return False
    return True


def is_30_minutes(start: datetime, end: datetime):
    return (end-start).seconds == 1800

def is_date_aware(d: datetime):
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None

def is_date_passed(d: datetime):
    return datetime.now() > d

def is_now_in_range(start: datetime, end: datetime):
    now = datetime.now()
    return now >= start and now < end

def is_datetime_in_range(dt: datetime, start: datetime, end: datetime):
    return dt >= start and dt < end

def get_seconds_until(dt: datetime) -> int:
    now = datetime.now()
    delta = dt - now
    return int(delta.total_seconds())