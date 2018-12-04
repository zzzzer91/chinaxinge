

from lib.db import truncate_table
from config import *


def test() -> None:
    truncate_table(MYSQL_CONFIG, MYSQL_TABLE_SAVE_POST[0])


if __name__ == '__main__':
    test()
