from enum import Enum


class SortOrder(str, Enum):
    """ソート順"""
    asc = "asc"
    desc = "desc"
