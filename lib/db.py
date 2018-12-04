"""数据库相关操作。

Created：2018-11-7
Modified：2018-11-7
"""

import pymysql

from lib.types import *


def insert_data(mysql_config: MysqlConfig, sql: str, item: Dict) -> int:
    """插入数据。"""

    mysql_conn = pymysql.connect(
        host=mysql_config['host'], port=mysql_config['port'],
        user=mysql_config['user'], password=mysql_config['pwd'],
        db=mysql_config['db'], autocommit=True
    )
    cursor = mysql_conn.cursor()

    cursor.execute(sql, item)

    cursor.close()
    mysql_conn.close()

    return cursor.lastrowid


def read_data(mysql_config: MysqlConfig, sql: str) -> List[Tuple]:
    """读取数据。"""

    mysql_conn = pymysql.connect(
        host=mysql_config['host'], port=mysql_config['port'],
        user=mysql_config['user'], password=mysql_config['pwd'],
        db=mysql_config['db']
    )
    cursor = mysql_conn.cursor()

    cursor.execute(sql)

    cursor.close()
    mysql_conn.close()

    return cursor.fetchall()


def truncate_table(mysql_config: MysqlConfig, table: str) -> None:
    """清空指定表。"""

    mysql_conn = pymysql.connect(
        host=mysql_config['host'], port=mysql_config['port'],
        user=mysql_config['user'], password=mysql_config['pwd'],
        db=mysql_config['db']
    )
    cursor = mysql_conn.cursor()

    cursor.execute(f'TRUNCATE TABLE {table}')

    cursor.close()
    mysql_conn.close()
