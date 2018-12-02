"""所用到的类型。

Created：2018-10-6
Modified：2018-10-6
"""

import datetime
from typing import Tuple, Dict, FrozenSet, Optional, Union, Pattern, List, Iterator, Type

__all__ = [
    'Tuple', 'List', 'Dict', 'FrozenSet', 'Type', 'Optional',
    'Iterator', 'Union', 'Pattern',
    'MysqlConfig', 'PostDetailDict'
]

MysqlConfig = Dict[str, Union[str, int]]
PostDetailDict = Dict[str, Union[str, int, datetime.datetime, None]]
