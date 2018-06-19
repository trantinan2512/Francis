from dateparser import parse
from datetime import datetime


def check_delay(timestamp, delay):
    """Return True if 'timestamp' has passed an amount of 'delay' or higher, False otherwise.
    And the time passed in rounded to 0.x
    - timestamp: 'str' type that can be parsed
    - delay: 'int' type, in seconds"""
    try:
        timestamp = parse(timestamp)
        now = datetime.now()
        time_passed = (now - timestamp).total_seconds()
        return (time_passed > delay), round((delay - time_passed), 1)
    # parsing timestamp returns None
    except TypeError:
        return None, None
