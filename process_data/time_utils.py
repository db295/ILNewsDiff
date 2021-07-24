import time
import datetime


def convert_str_to_timestamp(time_str) -> float:
    return time.mktime(datetime.datetime.strptime(time_str,
                                                  "%Y-%m-%d %H:%M:%S.%f").timetuple())
