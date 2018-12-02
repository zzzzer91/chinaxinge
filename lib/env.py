"""库配置。

Created：2018-9-29
Modified：2018-10-1
"""

import os

__all__ = [
    'LIB_ROOT', 'DICT_PATH', 'PER_REQUEST_TRY_COUNT'
]

# 此库所在目录
LIB_ROOT: str = os.path.dirname(__file__)

# 字典文件所在目录
DICT_PATH: str = os.path.abspath(os.path.join(LIB_ROOT, '../dict'))

# 请求失败后, 尝试次数
PER_REQUEST_TRY_COUNT: int = 4


def test() -> None:
    print(LIB_ROOT)
    print(DICT_PATH)


if __name__ == '__main__':
    test()
