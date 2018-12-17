"""用于提取和过滤的关键字。

Created：2018-8-28
Modified：2018-10-6
"""

import os

from lib import env
from lib.types import FrozenSet


with open(os.path.join(env.DICT_PATH, 'title.txt')) as f:
    lst = f.read().split('\n\n')
# 文章标题，满足任意两 group，则匹配成功
TITLE_ELIMINATE: FrozenSet[str] = frozenset(lst[0].split('\n'))  # 过滤词
TITLE_GROUP1: FrozenSet[str] = frozenset(lst[1].split('\n'))     # 需要关键字组1
TITLE_GROUP2: FrozenSet[str] = frozenset(lst[2].split('\n'))     # 需要关键字组2
TITLE_GROUP3: FrozenSet[str] = frozenset(lst[3].split('\n'))     # 需要关键字组3
TITLE_QINGPENG: FrozenSet[str] = frozenset(lst[4].split('\n'))   # 清棚
TITLE_SHANGLONG: FrozenSet[str] = frozenset(lst[5].split('\n'))  # 决赛上笼

with open(os.path.join(env.DICT_PATH, 'col_name.txt')) as f:
    lst = f.read().split('\n\n')
# 文章内容的可能列名
COL_NO: FrozenSet[str] = frozenset(lst[0].split('\n'))           # 排名
COL_NAME: FrozenSet[str] = frozenset(lst[1].split('\n'))         # 鸽主姓名
COL_AREA: FrozenSet[str] = frozenset(lst[2].split('\n'))         # 鸽主地址
COL_NUMBER: FrozenSet[str] = frozenset(lst[3].split('\n'))       # 足环号
COL_FEATHER: FrozenSet[str] = frozenset(lst[4].split('\n'))      # 羽色
COL_SPEED: FrozenSet[str] = frozenset(lst[5].split('\n'))        # 分速
COL_TIME: FrozenSet[str] = frozenset(lst[6].split('\n'))         # 归巢时间
COL_NO2: FrozenSet[str] = frozenset(lst[7].split('\n'))           # 排名
COL_COUNT_MUST: int = 2                                          # 必须列数量

del lst


def test() -> None:

    print(TITLE_QINGPENG, TITLE_SHANGLONG, TITLE_ELIMINATE,
          TITLE_GROUP1, TITLE_GROUP2, TITLE_GROUP3)
    print(COL_NO, COL_NAME, COL_AREA,
          COL_NUMBER, COL_FEATHER, COL_SPEED, COL_TIME,
          COL_NO2)


if __name__ == '__main__':
    test()
