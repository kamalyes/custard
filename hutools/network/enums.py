from enum import IntEnum


class ReqBodyTypeEnum(IntEnum):
    none = 0
    json = 1
    form = 2
    x_form = 3
    binary = 4
    graphQL = 5
