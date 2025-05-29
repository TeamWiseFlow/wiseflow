# don't be evil
# for commercial use, please contact to get permission
# wiseflow opensouce do not support commercial use since 4.0


import time
from datetime import datetime, timedelta, timezone


def get_current_timestamp() -> int:
    """
    获取当前的时间戳(13 位)：1701493264496
    :return:
    """
    return int(time.time() * 1000)


def get_current_time(time_format: str = "%Y-%m-%d %X") -> str:
    """
    获取当前的时间：'2023-12-02 13:01:23'
    Args:
        time_format: 时间格式

    Returns:

    """
    return time.strftime(time_format, time.localtime())


def get_current_date() -> str:
    """
    获取当前的日期：'2023-12-02'
    :return:
    """
    return time.strftime('%Y-%m-%d', time.localtime())


def get_time_str_from_unix_time(unixtime):
    """
    unix 整数类型时间戳  ==> 字符串日期时间
    :param unixtime:
    :return:
    """
    if int(unixtime) > 1000000000000:
        unixtime = int(unixtime) / 1000
    return time.strftime('%Y-%m-%d %X', time.localtime(unixtime))


def get_date_str_from_unix_time(unixtime):
    """
    unix 整数类型时间戳  ==> 字符串日期
    :param unixtime:
    :return:
    """
    if int(unixtime) > 1000000000000:
        unixtime = int(unixtime) / 1000
    return time.strftime('%Y-%m-%d', time.localtime(unixtime))


def get_unix_time_from_time_str(time_str):
    """
    字符串时间 ==> unix 整数类型时间戳，精确到秒
    :param time_str:
    :return:
    """
    try:
        format_str = "%Y-%m-%d %H:%M:%S"
        tm_object = time.strptime(str(time_str), format_str)
        return int(time.mktime(tm_object))
    except Exception as e:
        return 0
    pass


def get_unix_timestamp():
    return int(time.time())


def rfc2822_to_china_datetime(rfc2822_time):
    # 定义RFC 2822格式
    rfc2822_format = "%a %b %d %H:%M:%S %z %Y"

    # 将RFC 2822时间字符串转换为datetime对象
    dt_object = datetime.strptime(rfc2822_time, rfc2822_format)

    # 将datetime对象的时区转换为中国时区
    dt_object_china = dt_object.astimezone(timezone(timedelta(hours=8)))
    return dt_object_china


def rfc2822_to_timestamp(rfc2822_time):
    # 定义RFC 2822格式
    rfc2822_format = "%a %b %d %H:%M:%S %z %Y"

    # 将RFC 2822时间字符串转换为datetime对象
    dt_object = datetime.strptime(rfc2822_time, rfc2822_format)

    # 将datetime对象转换为UTC时间
    dt_utc = dt_object.replace(tzinfo=timezone.utc)

    # 计算UTC时间对应的Unix时间戳
    timestamp = int(dt_utc.timestamp())

    return timestamp


def is_cacheup(millisecond_timestamp: int | str, nhour: int) -> bool:
    """
    判断给定的毫秒级时间戳是否在当前时间的 nhour 小时之内（基于时间间隔）。

    Args:
        millisecond_timestamp: 毫秒级时间戳 (13 位整数)。
        nhour: 小时数（非负整数），用于判断时间戳是否在此小时数范围内。

    Returns:
        如果时间戳在当前时间的 nhour 小时之内，返回 True；否则返回 False。
    """

    if not isinstance(nhour, int) or nhour < 0:
        return False
    
    if not isinstance(millisecond_timestamp, int):
        try:
            millisecond_timestamp = int(millisecond_timestamp)
        except Exception as e:
            return False
        
    if millisecond_timestamp < 1000000000000:
        millisecond_timestamp = millisecond_timestamp * 1000

    try:
        # 获取当前的毫秒级时间戳
        current_timestamp = get_current_timestamp()

        if millisecond_timestamp > current_timestamp:
            return False

        # 计算时间戳之间的差值（取绝对值）
        time_difference_ms = abs(millisecond_timestamp - current_timestamp)

        # 将 nhour 转换为毫秒
        hour_threshold_ms = nhour * 60 * 60 * 1000

        # 判断差值是否在 nhour 小时之内
        return time_difference_ms <= hour_threshold_ms
    except Exception as e:
        # 处理可能的异常
        print(f"Error processing timestamp {millisecond_timestamp} or nhour {nhour}: {e}")
        return False


if __name__ == '__main__':
    # 示例用法
    _rfc2822_time = "Sat Dec 23 17:12:54 +0800 2023"
    print(rfc2822_to_china_datetime(_rfc2822_time))

    # 示例：判断毫秒级时间戳是否在当前时间的 nhour 小时之内
    _current_timestamp = get_current_timestamp() # 当前时间戳
    _one_hour_ago = _current_timestamp - 60 * 60 * 1000 # 一小时前的时间戳
    _two_hours_ago = _current_timestamp - 2 * 60 * 60 * 1000 # 两小时前的时间戳
    _one_hour_later = _current_timestamp + 60 * 60 * 1000 # 一小时后的时间戳

    nhour_test = 1

    print(f"判断时间戳 {_current_timestamp} (现在) 是否在距今 {nhour_test} 小时内: {is_cacheup(_current_timestamp, nhour_test)}")
    print(f"判断时间戳 {_one_hour_ago} (一小时前) 是否在距今 {nhour_test} 小时内: {is_cacheup(_one_hour_ago, nhour_test)}")
    print(f"判断时间戳 {_two_hours_ago} (两小时前) 是否在距今 {nhour_test} 小时内: {is_cacheup(_two_hours_ago, nhour_test)}")
    print(f"判断时间戳 {_one_hour_later} (一小时后) 是否在距今 {nhour_test} 小时内: {is_cacheup(_one_hour_later, nhour_test)}")

    nhour_test_zero = 0
    print(f"判断时间戳 {_current_timestamp} (现在) 是否在距今 {nhour_test_zero} 小时内: {is_cacheup(_current_timestamp, nhour_test_zero)}")
    print(f"判断时间戳 {_one_hour_ago} (一小时前) 是否在距今 {nhour_test_zero} 小时内: {is_cacheup(_one_hour_ago, nhour_test_zero)}")
