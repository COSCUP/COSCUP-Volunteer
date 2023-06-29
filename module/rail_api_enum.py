"""This file stores all enum classes used for API"""
import enum


class TrainType(enum.IntEnum):
    """Train Type

    Args:
        enum (int): Type of train
    """

    TARKO = 1  # 太魯閣
    PUYUMA = 2  # 普悠瑪
    TZECHIANG = 3  # 自強
    CHUKUANG = 4  # 莒光
    FUHSING = 5  # 復興
    LOCAL = 6  # 區間
    ORDINARY = 7  # 普快
    LOCAL_FAST = 10  # 區間快


class TicketType(enum.IntEnum):
    """Ticket Type

    Args:
        enum (int): Type of ticket
    """

    NORMAL = 1  # 一般票
    RETURN = 2  # 來回票
    ELECTRONIC = 3  # 電子票證
    MULTIRIDE = 4  # 回數票
    PREPAID_30DAYS = 5  # 定期票 (30天)
    PREPAID_60DAYS = 6  # 定期票 (60天)
    EARLY_BIRD = 7  # 早鳥票


class FareClass(enum.IntEnum):
    """Ticket Fare Class

    Args:
        enum (int): Class of ticket fare
    """

    ADULT = 1  # 成人
    STUDENT = 2  # 學生
    CHILD = 3  # 孩童
    SENIOR = 4  # 敬老
    DISABLED = 5  # 愛心
    DISABLED_CHILDREN = 6  # 愛心孩童
    DISABLED_ACCOMPANY = 7  # 愛心優待/愛心陪伴
    GROUP = 8  # 團體
    MILITARY = 9  # 軍警


class CabinClass(enum.IntEnum):
    """Carbin Class

    Args:
        enum (int): Class of carbin
    """

    RESERVED = 1  # 標準座車廂
    BUSINESS = 2  # 商務座車廂
    NON_RESERVED = 3  # 自由座車廂
